import os
import xml.etree.ElementTree as ET

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from wagtail_xliff_translation.forms import DownloadForm, ImportForm
from wagtail_xliff_translation.helpers.page import PageHelper


def test_download_view_get(admin_client, page):
    resp = admin_client.get(reverse("xliff:download", kwargs={"page_id": page.pk}))
    assert isinstance(resp.context["form"], DownloadForm)


def test_download_view_post(admin_client, page, locale_factory):
    german = locale_factory(language_code="de")
    resp = admin_client.post(
        reverse("xliff:download", kwargs={"page_id": page.pk}), {"language": german.pk}
    )
    assert resp.status_code == 200


def test_upload_view_get(admin_client, page):
    resp = admin_client.get(reverse("xliff:upload", kwargs={"page_id": page.pk}))
    assert isinstance(resp.context["form"], ImportForm)


def test_upload_view_post(admin_client, home_en, locale_factory):
    locale_factory(language_code="de")
    upload_file = open(
        os.path.join(settings.BASE_DIR, "test_app/data/xliff_translated/zgpage.xliff"),
        "rb",
    )
    # set page pk
    xml_string = upload_file.read()
    xml_tree = ET.fromstring(xml_string)
    for file_element in xml_tree.findall("file"):
        file_element.set("id", PageHelper.get_object_id(home_en))
    xml_string = ET.tostring(xml_tree, encoding="unicode")
    # ET removes not loaded namespaces
    xml_string = xml_string.replace("ns0", "mda")

    resp = admin_client.post(
        reverse("xliff:upload", kwargs={"page_id": home_en.pk}),
        {
            "xliff": SimpleUploadedFile(upload_file.name, xml_string.encode()),
            "update_target_page": True,
            "update_subtree": True,
            "create_pages": True,
        },
    )
    assert resp.url == reverse("wagtailadmin_explore", args=[home_en.pk])
    assert resp.status_code == 302
