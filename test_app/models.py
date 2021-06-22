from django.db import models

from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock

from . import blocks as test_blocks


class PageWithRichText(Page):
    test_textfield = models.TextField(blank=True)
    test_richtextfield = RichTextField(blank=True)


class PageWithStreamField(Page):
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

    content_panels = Page.content_panels + [StreamFieldPanel("test_streamfield")]
