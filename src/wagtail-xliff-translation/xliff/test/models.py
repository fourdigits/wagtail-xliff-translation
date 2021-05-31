from django.db import models

from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.documents.blocks import DocumentChooserBlock

from zg.django.website.models import RichTextField, StreamFieldPanel, ZGPage
from zg.django.xliff.test import blocks as test_blocks


class PageWitRichText(ZGPage):
    test_textfield = models.TextField(blank=True)
    test_richtextfield = RichTextField(blank=True)


class PageWithStreamField(ZGPage):
    test_streamfield = StreamField(
        [
            ("char_block", blocks.CharBlock(max_length=255)),
            ("boolean_block", blocks.BooleanBlock()),
            ("text_block", blocks.TextBlock()),
            ("email_block", blocks.EmailBlock()),
            ("url_block", blocks.URLBlock()),
            ("rich_text_block", blocks.RichTextBlock()),
            ("raw_html_block", blocks.RawHTMLBlock()),
            ("blockquote_block", blocks.BlockQuoteBlock()),
            ("struct_block", test_blocks.RegularStructBlock()),
            ("rich_text_struct_block", test_blocks.RichTextStructBlock()),
            ("nested_struct_block", test_blocks.NestedStructBlock()),
            ("list_block", blocks.ListBlock(blocks.TextBlock())),
            (
                "list_block_with_struct_block",
                blocks.ListBlock(test_blocks.RegularStructBlock()),
            ),
            ("stream_block", test_blocks.RegularStreamBlock()),
            ("nested_streamblock", test_blocks.NestedStreamBlock()),
            ("stream_block_with_struct_block", test_blocks.StreamWithStructBlock()),
            ("document_block", DocumentChooserBlock()),
        ],
        blank=True,
    )

    content_panels = ZGPage.content_panels + [StreamFieldPanel("test_streamfield")]
