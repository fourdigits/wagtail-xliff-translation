from wagtail_xliff_translation.parsers.xliff_wagtail import XliffWagtailParser
import pytest

from django.core import serializers
from django.core.serializers.base import DeserializationError

from ..utils import get_condensed_sample_data, get_object_ids

pytestmark = pytest.mark.django_db
pytestmark = pytest.mark.skip

def test_basic_deserialization(english_german_base, page_factory):
    site, english_page, german_language = english_german_base
    object_ids = get_object_ids([english_page])
    xliff = get_condensed_sample_data("xliff_translated/zgpage.xliff", object_ids)
    translated_pages = serializers.deserialize(
        "xliff", xliff, object_ids=object_ids, create_pages=True
    ).all()
    german_page = translated_pages[0]
    assert german_page.draft
    assert german_page.title == german_page.slug == "german_page"

    new_parent_page = page_factory()
    with pytest.raises(DeserializationError):
        serializers.deserialize(
            "xliff",
            xliff,
            object_ids=object_ids,
            create_pages=True,
            parent_page=new_parent_page,
        ).all(),
        "Manually setting a parent page only works if the page has no translations yet",

    german_page.delete()
    translated_pages = serializers.deserialize(
        "xliff",
        xliff,
        object_ids=object_ids,
        create_pages=True,
        parent_page=new_parent_page,
    ).all()
    assert translated_pages[0].get_parent() == new_parent_page


def test_richtext_deserialization(english_richtext_german_base):
    site, english_page, german_language = english_richtext_german_base
    object_ids = get_object_ids([english_page])
    xliff = get_condensed_sample_data("xliff_translated/richtextpage.xliff", object_ids)
    translated_pages = serializers.deserialize(
        "xliff", xliff, object_ids=object_ids, create_pages=True
    ).all()
    german_page = translated_pages[0]
    assert (
        german_page.test_textfield
        == "ein längerer Satz mit viel Inhalt\\nmit neuen Zeilen gespeichert\\nund noch ein paar neue Zeilen"
    )
    assert (
        german_page.test_richtextfield
        == '<h1>hoeba_german</h1><img href="/link-to-kek/" /><img/><a href="/link-to-kek/">kek_german</a><bold>Lust auf kühnes Zeug</bold>'
    )


def test_streamfield_deserialization(english_streamfield_german_base):
    site, english_page, german_language = english_streamfield_german_base
    object_ids = get_object_ids([english_page])
    xliff = get_condensed_sample_data(
        "xliff_translated/streamfieldpage.xliff", object_ids
    )
    translated_pages = serializers.deserialize(
        "xliff", xliff, object_ids=object_ids, create_pages=True
    ).all()
    german_page = translated_pages[0]
    assert german_page.test_streamfield[0].value == "german text"
    assert german_page.test_streamfield[1].value
    assert german_page.test_streamfield[2].value == "german text"
    assert german_page.test_streamfield[3].value == "test@test.de"
    assert german_page.test_streamfield[4].value == "http://www.fourdigits.de"
    assert (
        str(german_page.test_streamfield[5].value)
        == '<div class="rich-text">schöner richtext</div>'
    )
    assert german_page.test_streamfield[6].value == "rohhtmlblock"
    assert german_page.test_streamfield[7].value == "ein Blockzitat"
    assert (
        german_page.test_streamfield[8].value.get("field_a")
        == "einfaches Strukturfeld a"
    )
    assert (
        german_page.test_streamfield[8].value.get("field_b")
        == "einfaches Strukturfeld b"
    )
    assert (
        str(german_page.test_streamfield[9].value.get("field_a"))
        == '<div class="rich-text"><p><b>Rich-Text-Strukturblock</b></p></div>'
    )
    assert (
        str(german_page.test_streamfield[9].value.get("field_b"))
        == '<div class="rich-text"><p><b>Rich-Text-Strukturblock</b></p></div>'
    )
    assert (
        german_page.test_streamfield[10].value.get("child").get("field_a")
        == "verschachteltes Strukturblockfeld a"
    )
    assert (
        german_page.test_streamfield[10].value.get("child").get("field_b")
        == "verschachteltes Strukturblockfeld b"
    )
    assert german_page.test_streamfield[11].value == ["Liste mit Text"]
    assert (
        german_page.test_streamfield[12].value[0].get("field_a")
        == "Feld a im Listenblock"
    )
    assert (
        german_page.test_streamfield[12].value[0].get("field_b")
        == "Feld b im Listenblock"
    )
    assert (
        german_page.test_streamfield[12].value[1].get("field_a")
        == "Feld a im Listenblock"
    )
    assert (
        german_page.test_streamfield[12].value[1].get("field_b")
        == "Feld b im Listenblock"
    )
    assert german_page.test_streamfield[13].value[0].value == "mit eines char block"
    assert (
        german_page.test_streamfield[14].value[0].value[0].value
        == "sehr viel verschachtelter Zeichenblock"
    )
    assert (
        german_page.test_streamfield[15].value[0].value.get("field_a")
        == "verschachteltes Feld a"
    )
    assert (
        german_page.test_streamfield[15].value[0].value.get("field_b")
        == "verschachteltes Feld b"
    )
