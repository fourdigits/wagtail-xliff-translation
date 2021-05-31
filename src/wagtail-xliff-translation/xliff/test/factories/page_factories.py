import json
import os

import factory

from django.conf import settings

from wagtail.core.rich_text import RichText

from zg.django.website.factories import ZGPageFactory
from zg.django.xliff.test.models import PageWithStreamField, PageWitRichText


class PageWitRichTextFactory(ZGPageFactory):
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


class PageWithStreamFieldFactory(ZGPageFactory):
    class Meta:
        model = PageWithStreamField

    @factory.lazy_attribute
    def test_streamfield(self):
        # wagtail factories as of now doesn't supported streamblock nor nested block structures
        # using a .json as seed data is deemed as the most stable solution for catching every streamfield edge case
        data_path = os.path.join(
            settings.BASE_DIR, "xliff/test/factories/streamfield_data.json"
        )
        with open(data_path) as json_file:
            loaded = json.load(json_file)
            return json.dumps(loaded)
