import pytest

from django.db.models import DurationField

from ...helpers.page import PageHelper

pytestmark = pytest.mark.django_db


def test_optional_translate(page_factory):
    page = page_factory()
    page_helper = PageHelper(page)
    setattr(page, "translatable_fields", [DurationField.__name__])
    assert page_helper.verify_translatable(DurationField)
