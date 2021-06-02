import json
import os
from django.utils.translation import get_language

import factory

import wagtail_factories
from django.conf import settings
from django.utils.text import slugify

from wagtail.core.rich_text import RichText
from wagtail.core.models import Locale, Page

from ..models import PageWithStreamField, PageWithRichText


class LocaleFactory(factory.django.DjangoModelFactory):
    language_code = factory.LazyFunction(get_language)

    class Meta:
        model = Locale
        django_get_or_create = ("language_code",)


class PageFactory(wagtail_factories.PageFactory):
    locale = factory.SubFactory(LocaleFactory)
    title = "Test page"
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))
    path = factory.Sequence(lambda n=1: f"00010001000{n}")
    depth = 2

    # path = "000100010001"
    # depth = 2
    
    class Meta:
        model = Page
        django_get_or_create = ("slug",)

class PageWithRichTextFactory(PageFactory):
    class Meta:
        model = PageWithRichText

    test_textfield = "a longer sentence with a lot of content"
    test_richtextfield = RichText(
        """
        <h1>hoeba</h1>
        <img href='/link-to-kek/' />
        <a href='http://google.nl'>kek</a>
        <bold>fancy bold stuff</bold>
        """
    )


class PageWithStreamFieldFactory(PageFactory):
    class Meta:
        model = PageWithStreamField

    @factory.lazy_attribute
    def test_streamfield(self):
        # wagtail factories as of now doesn't supported streamblock nor nested block structures
        # using a .json as seed data is deemed as the most stable solution for catching every streamfield edge case
        data_path = os.path.join(
            settings.BASE_DIR, "test_app/factories/streamfield_data.json"
        )
        with open(data_path) as json_file:
            loaded = json.load(json_file)
            return json.dumps(loaded)
