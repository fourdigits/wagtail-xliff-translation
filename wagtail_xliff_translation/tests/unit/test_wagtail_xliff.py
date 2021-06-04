import pytest

from django.core import serializers
from django.core.serializers.base import SerializationError

pytestmark = pytest.mark.django_db


def test_all_translatable_page(locale_factory):
    german = locale_factory(language_code="de")
    with pytest.raises(SerializationError) as err:
        serializers.serialize("xliff", [object], target_language=german.language_code)
    assert str(err.value) == "all instances must be of type Page"


def test_all_same_src_language(english_german_translated):
    english_page, german_page = english_german_translated
    with pytest.raises(SerializationError) as err:
        serializers.serialize(
            "xliff",
            [english_page, german_page],
            target_language=german_page.locale.language_code,
        )
    assert str(err.value) == "all instances must have the same source language"


def test_invalid_target_language(page):
    with pytest.raises(SerializationError) as err:
        serializers.serialize("xliff", [page], target_language="zz")
    assert str(err.value) == "invalid target language"
