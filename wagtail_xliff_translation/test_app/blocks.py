from wagtail.core import blocks


class RegularStructBlock(blocks.StructBlock):
    field_a = blocks.TextBlock()
    field_b = blocks.TextBlock()


class RichTextStructBlock(blocks.StructBlock):
    field_a = blocks.RichTextBlock()
    field_b = blocks.RichTextBlock()


class NestedStructBlock(blocks.StructBlock):
    child = RegularStructBlock()


class RegularStreamBlock(blocks.StreamBlock):
    char_block = blocks.CharBlock(max_length=255)


class NestedStreamBlockChild(blocks.StreamBlock):
    char_block = blocks.CharBlock(max_length=255)


class NestedStreamBlock(blocks.StreamBlock):
    child = NestedStreamBlockChild()


class StreamWithStructBlock(blocks.StreamBlock):
    child = RegularStructBlock()
