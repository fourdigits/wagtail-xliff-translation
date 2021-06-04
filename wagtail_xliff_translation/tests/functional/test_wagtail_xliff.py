import pytest

from django.core import serializers

from ..utils import sample_data_equals

pytestmark = pytest.mark.django_db


def test_basic_serialization(english_german_base):
    page, german_language = english_german_base
    serialized_page = serializers.serialize(
        "xliff", [page], target_language=german_language.language_code
    )
    assert sample_data_equals(serialized_page, "xliff/zgpage.xliff")


def test_richtext_serialization(english_richtext_german_base):
    page, german_language = english_richtext_german_base
    serialized_page = serializers.serialize(
        "xliff", [page], target_language=german_language.language_code
    )
    assert sample_data_equals(serialized_page, "xliff/richtextpage.xliff")


def test_streamfield_serialization(english_streamfield, locale_factory):
    english_page = english_streamfield
    german_language = locale_factory(language_code="de")
    serialized_page = serializers.serialize(
        "xliff", [english_page], target_language=german_language.language_code
    )
    assert sample_data_equals(serialized_page, "xliff/streamfieldpage.xliff")
