import pytest

from django.core import serializers

from ..utils import sample_data_equals

pytestmark = pytest.mark.django_db
pytestmark = pytest.mark.skip


@pytest.mark.skip(reason="Needs a fix")
def test_basic_serialization(english_german_base):
    site, page, german_language = english_german_base
    serialized_page = serializers.serialize(
        "xliff", [page], target_language=german_language.code
    )
    assert sample_data_equals(serialized_page, "xliff/zgpage.xliff")


@pytest.mark.skip(reason="Needs a fix")
def test_richtext_serialization(english_richtext_german_base):
    site, page, german_language = english_richtext_german_base
    serialized_page = serializers.serialize(
        "xliff", [page], target_language=german_language.code
    )
    assert sample_data_equals(serialized_page, "xliff/richtextpage.xliff")


def test_streamfield_serialization(english_streamfield_german_base):
    site, page, german_language = english_streamfield_german_base
    serialized_page = serializers.serialize(
        "xliff", [page], target_language=german_language.code
    )
    assert sample_data_equals(serialized_page, "xliff/streamfieldpage.xliff")
