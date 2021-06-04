import os

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.serializers.base import DeserializationError, SerializationError
from django.urls import reverse

from wagtail.core.models import Page

from wagtail_xliff_translation.serializers.wagtail_xliff import WagtailXliffSerializer
from wagtail_xliff_translation.serializers.xliff_wagtail import XliffWagtailDeserializer

pytestmark = pytest.mark.django_db


def test_download_view_post_invalid(admin_client, page):
    resp = admin_client.post(reverse("xliff:download", kwargs={"page_id": page.pk}))
    form = resp.context["form"]
    assert form.errors["language"][0] == "This field is required."


def test_download_view_with_descendants(admin_client, page):
    page.add_child(instance=Page(title="descendant"))
    resp = admin_client.get(reverse("xliff:download", kwargs={"page_id": page.pk}))
    assert "include_subtree" in resp.context["form"].fields


def test_download_view_with_included_subtree(admin_client, page, locale_factory):
    german = locale_factory(language_code="de")
    page.add_child(instance=Page(title="Sub"))
    resp = admin_client.post(
        reverse("xliff:download", kwargs={"page_id": page.pk}),
        {"language": german.pk, "include_subtree": True},
    )
    assert resp.status_code == 200


def test_download_view_without_admin_rights(client, page):
    user = get_user_model().objects.create_user(
        username="username", password="password"
    )
    editor_group = Group.objects.get(name="Editors")
    editor_group.user_set.add(user)
    client.force_login(user)
    resp = client.get(reverse("xliff:download", kwargs={"page_id": page.pk}))
    assert resp.status_code == 302
    assert resp.url == "/admin/"


def test_download_view_serialization_error(admin_client, page, locale_factory, mocker):
    german = locale_factory(language_code="de")
    test_error = "test error"
    mocker.patch.object(
        WagtailXliffSerializer, "serialize", side_effect=SerializationError(test_error)
    )
    resp = admin_client.post(
        reverse("xliff:download", kwargs={"page_id": page.pk}), {"language": german.pk}
    )
    messages = list(resp.context["messages"])
    assert messages[0].message == test_error
    assert resp.status_code == 200


def test_upload_view_post_deserialization_error(admin_client, page, mocker):
    test_error = "test_error"
    filename = os.path.join(settings.BASE_DIR, "test_app/data/xliff/zgpage.xliff")
    upload_file = open(os.path.join(filename), "rb")
    mocker.patch.object(
        XliffWagtailDeserializer, "all", side_effect=DeserializationError(test_error)
    )
    resp = admin_client.post(
        reverse("xliff:upload", kwargs={"page_id": page.pk}),
        {
            "xliff": SimpleUploadedFile(upload_file.name, upload_file.read()),
            "update_target_page": True,
            "update_subtree": True,
            "create_pages": True,
        },
    )
    messages = list(resp.context["messages"])
    assert messages[0].message == test_error
    assert resp.status_code == 200


def test_upload_view_post_invalid(admin_client, page):
    resp = admin_client.post(
        reverse("xliff:upload", kwargs={"page_id": page.pk}),
        {
            "xliff": "xliff_mock",
            "update_target_page": False,
            "update_subtree": False,
            "create_pages": True,
        },
    )
    assert resp.status_code == 200
