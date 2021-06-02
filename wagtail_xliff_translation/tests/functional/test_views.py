import os
import xml.etree.ElementTree as ET

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from wagtail_xliff_translation.forms import DownloadForm, ImportForm
from wagtail_xliff_translation.helpers.page import PageHelper


def test_download_view_get(admin_client, page_factory):
    page = page_factory()
    resp = admin_client.get(reverse("xliff:download", kwargs={"page_id": page.pk}))
    breakpoint()
    assert isinstance(resp.context["form"], DownloadForm)


def test_download_view_post(admin_client, page_factory, language_factory):
    page = page_factory()
    german = language_factory(code="de")
    resp = admin_client.post(
        reverse("xliff:download", kwargs={"page_id": page.pk}), {"language": german.pk}
    )
    assert resp.status_code == 200


def test_upload_view_get(admin_client, page_factory):
    page = page_factory()
    resp = admin_client.get(reverse("xliff:upload", kwargs={"page_id": page.pk}))
    assert isinstance(resp.context["form"], ImportForm)


def test_upload_view_post(
    admin_client, page_factory, site_factory, language_factory
):
    site = site_factory()
    parent = page_factory(parent=site.root_page)
    page = page_factory(parent=parent)
    de_lang = language_factory(code="de")
    german_parent = parent.create_translation(
        de_lang, copy_fields=True, parent=parent.get_parent()
    )
    upload_file = open(
        os.path.join(
            settings.BASE_DIR, "xliff/tests/data/xliff_translated/zgpage.xliff"
        ),
        "rb",
    )
    # set page pk
    xml_string = upload_file.read()
    xml_tree = ET.fromstring(xml_string)
    for file_element in xml_tree.findall("file"):
        file_element.set("id", PageHelper.get_object_id(page))
    xml_string = ET.tostring(xml_tree, encoding="unicode")
    # ET removes onloaded namespaces
    xml_string = xml_string.replace("ns0", "mda")

    resp = admin_client.post(
        reverse("xliff:upload", kwargs={"page_id": page.pk}),
        {
            "xliff": SimpleUploadedFile(upload_file.name, xml_string.encode()),
            "update_target_page": True,
            "update_subtree": True,
            "create_pages": True,
            "parent_page": german_parent.id,
        },
    )
    assert resp.url == reverse("wagtailadmin_explore", args=[page.pk])
    assert resp.status_code == 302
