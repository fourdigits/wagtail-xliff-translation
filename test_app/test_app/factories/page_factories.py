import json
import os
from django.utils.translation import get_language

import factory

from wagtail_factories import PageFactory
from django.conf import settings

from wagtail.core.rich_text import RichText
from wagtailtrans.models import Language

from ..models import PageWithStreamField, PageWitRichText


class PageWitRichTextFactory(PageFactory):
    class Meta:
        model = PageWitRichText

    test_textfield = "a longer sentence with a lot of content"
    test_richtextfield = RichText(
        """
        <h1>hoeba</h1>
        <img href='/link-to-kek/' />
        <a href='/link-to-kek/'>kek</a>
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


class LanguageFactory(factory.django.DjangoModelFactory):
    code = factory.LazyFunction(get_language)
    position = 0
    is_default = True
    live = True

    class Meta:
        model = Language
        django_get_or_create = ("code",)