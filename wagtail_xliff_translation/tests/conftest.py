import json
import os

import pytest
import wagtail_factories
from pytest_factoryboy import register
from test_app.factories import LocaleFactory
from test_app.models import PageWithRichText, PageWithStreamField

from django.conf import settings

from wagtail.core.models import Page, Site
from wagtail.core.rich_text import RichText

from wagtail_xliff_translation.parsers.html_xliff import HtmlXliffParser

register(LocaleFactory)
register(wagtail_factories.SiteFactory)
register(wagtail_factories.ImageFactory)
register(wagtail_factories.DocumentFactory)


@pytest.fixture
def html_parser():
    return HtmlXliffParser()


@pytest.fixture
def home_en():
    """Default root page is created by Wagtail migrations.
    It has the default locale (English)"""
    page = Site.objects.first().root_page
    assert page.locale.language_code == "en-us"
    return page


@pytest.fixture
def page(home_en):
    page = Page(title="english_page", slug="english_page")
    home_en.add_child(instance=page)
    return page


@pytest.fixture
def page_with_rich_text(home_en):
    page = PageWithRichText(
        title="english_richtext",
        test_textfield="a longer sentence with a lot of content",
        test_richtextfield=RichText(
            """
            <h1>hoeba</h1>
            <img href='/link-to-kek/' />
            <a href='http://google.nl'>kek</a>
            <bold>fancy bold stuff</bold>
            """
        ),
    )
    home_en.add_child(instance=page)
    return page


@pytest.fixture
def page_with_streamfield(home_en):
    # Use a .json as seed data is deemed as the most stable solution for catching every streamfield edge case.
    data_path = os.path.join(
        settings.BASE_DIR, "test_app/factories/streamfield_data.json"
    )
    with open(data_path) as json_file:
        loaded = json.load(json_file)
        data = json.dumps(loaded)

    page = PageWithStreamField(title="english_streamfield", test_streamfield=data)
    home_en.add_child(instance=page)
    return page


@pytest.fixture
def english_richtext(page_with_rich_text):
    return page_with_rich_text


@pytest.fixture
def english_streamfield(page_with_streamfield):
    return page_with_streamfield


@pytest.fixture
def english_base(page):
    return page, page.locale


@pytest.fixture
def english_german_base(page, locale_factory):
    german_language = locale_factory(language_code="de")
    return page, german_language


@pytest.fixture
def english_richtext_german_base(english_richtext, locale_factory):
    german_language = locale_factory(language_code="de")
    return english_richtext, german_language


@pytest.fixture
def english_streamfield_german_base(english_streamfield, locale_factory):
    german_language = locale_factory(language_code="de")
    return english_streamfield, german_language


@pytest.fixture
def english_german_translated(page, locale_factory):
    german_language = locale_factory(language_code="de")
    german_page = page.copy_for_translation(german_language, copy_parents=True)
    return page, german_page
