import pytest
import wagtail_factories
from pytest_factoryboy import register
from test_app.factories import (
    LocaleFactory,
    PageFactory,
    PageWithRichTextFactory,
    PageWithStreamFieldFactory,
)

from wagtail_xliff_translation.parsers.html_xliff import HtmlXliffParser

register(PageFactory)
register(PageWithRichTextFactory)
register(LocaleFactory)
register(wagtail_factories.SiteFactory)


@pytest.fixture
def html_parser():
    return HtmlXliffParser()


@pytest.fixture
def locale_factory():
    return LocaleFactory


@pytest.fixture
def page_with_streamfield_factory():
    return PageWithStreamFieldFactory


@pytest.fixture
def english_base(page_factory, site):
    parent = page_factory(parent=site.root_page)
    english_page = page_factory(
        parent=parent, title="english_page", slug="english_page"
    )
    return site, english_page


@pytest.fixture
def english_richtext(site, page_with_rich_text_factory):
    parent = page_with_rich_text_factory(parent=site.root_page)
    english_richtext = page_with_rich_text_factory(
        parent=parent, title="english_richtext", slug="english_richtext"
    )
    return site, english_richtext


@pytest.fixture
def english_streamfield(site, page_with_streamfield_factory):
    parent = page_with_streamfield_factory(parent=site.root_page)
    english_streamfield = page_with_streamfield_factory(
        parent=parent, title="english_richtext", slug="english_richtext"
    )
    return site, english_streamfield


@pytest.fixture
def english_german_base(english_base, locale_factory):
    site, english_page = english_base
    german_language = locale_factory(language_code="de")
    english_page.get_parent().copy_for_translation(german_language)
    return site, english_page, german_language


@pytest.fixture
def english_richtext_german_base(english_richtext, locale_factory):
    site, english_page = english_richtext
    german_language = locale_factory(language_code="de")
    english_page.get_parent().copy_for_translation(german_language)
    return site, english_page, german_language


@pytest.fixture
def english_streamfield_german_base(english_streamfield, locale_factory):
    site, english_page = english_streamfield
    german_language = locale_factory(code="de")
    english_page.copy_for_translation(german_language)
    return site, english_page, german_language


@pytest.fixture
def english_german_translated(english_german_base):
    site, english_page, german_language = english_german_base
    german_page = english_page.copy(
        to=site.root_page,
        update_attrs={"language": german_language, "slug": english_page.slug + "-de"},
    )
    return site, english_page, german_page
