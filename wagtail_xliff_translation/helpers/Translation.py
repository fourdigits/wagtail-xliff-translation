import json

from django.core.exceptions import ValidationError
from django.utils.text import slugify

from wagtail_xliff_translation.parsers.xliff_wagtail import XliffWagtailParser


class TranslationHelper:
    def __init__(self, page):
        self.page = page

    def translate_page(self, file_node, translation_target_page):
        self.xliff_parser = XliffWagtailParser(file_node)
        local_fields = self.xliff_parser.get_local_fields()
        stream_fields = self.xliff_parser.get_stream_fields()
        translated_page = translation_target_page
        if local_fields:
            translated_page = self.translate_local_fields(local_fields, translated_page)
        if stream_fields:
            translated_page = self.translate_stream_fields(
                stream_fields, translated_page
            )
        translated_page.draft = True
        try:
            translated_page.save_revision()
            translated_page.save()
        except ValidationError as error:
            error_fields = list([key for key in error.message_dict.keys()])
            raise ValidationError(
                f"Cannot properly import XLIFF. "
                f"There is a validation error for the translated page {translated_page.title}. "
                f"Error(s) on field(s): {error_fields}. Full error message: {error}"
            )
        return translated_page

    @staticmethod
    def translate_local_fields(local_fields, translated_page):
        translation_data = {field["name"]: field["target"] for field in local_fields}
        for attr, value in translation_data.items():
            if attr == "slug":
                value = slugify(value)
            setattr(translated_page, attr, value)
        return translated_page

    @staticmethod
    def translate_stream_fields(stream_fields, translated_page):
        for name, stream_field in stream_fields.items():
            setattr(translated_page, name, json.dumps(stream_field))
        return translated_page
