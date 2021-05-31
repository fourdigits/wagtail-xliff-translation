import pytest

from django.db.models import DurationField

from zg.django.xliff.helpers.page import PageHelper

pytestmark = pytest.mark.django_db


def test_optional_translate(zg_page_factory):
    page = zg_page_factory()
    page_helper = PageHelper(page)
    setattr(page, "translatable_fields", [DurationField.__name__])
    assert page_helper.verify_translatable(DurationField)
