import pytest
import wagtail_factories
from pytest_factoryboy import register
from test_app.factories import (
    LanguageFactory,
    PageFactory,
    PageWithRichTextFactory,
    PageWithStreamFieldFactory,
)

from wagtail_xliff_translation.parsers.html_xliff import HtmlXliffParser

register(PageFactory)
register(PageWithRichTextFactory)
register(LanguageFactory)
register(wagtail_factories.SiteFactory)


@pytest.fixture
def html_parser():
    return HtmlXliffParser()


@pytest.fixture
def language_factory():
    return LanguageFactory


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
def english_german_base(english_base, language_factory):
    site, english_page = english_base
    german_language = language_factory(code="de", is_default=False)
    english_page.get_parent().create_translation(
        german_language, copy_fields=True, parent=site.root_page
    )
    return site, english_page, german_language


@pytest.fixture
def english_richtext_german_base(english_richtext, language_factory):
    site, english_page = english_richtext
    german_language = language_factory(code="de", is_default=False)
    english_page.get_parent().create_translation(
        german_language, copy_fields=True, parent=site.root_page
    )
    return site, english_page, german_language


@pytest.fixture
def english_streamfield_german_base(english_streamfield, language_factory):
    site, english_page = english_streamfield
    german_language = language_factory(code="de", is_default=False)
    english_page.get_parent().create_translation(
        german_language, copy_fields=True, parent=site.root_page
    )
    return site, english_page, german_language


@pytest.fixture
def english_german_translated(english_german_base):
    site, english_page, german_language = english_german_base
    german_page = english_page.copy(
        to=site.root_page,
        update_attrs={"language": german_language, "slug": english_page.slug + "-de"},
    )
    return site, english_page, german_page
