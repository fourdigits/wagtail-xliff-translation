from django.utils.safestring import SafeText
from django.utils.xmlutils import SimplerXMLGenerator

from wagtail.core.fields import RichTextField
from wagtail.core.rich_text import RichText

from .constants import MetaAttributes, MetaGroupAttributes, XliffElements
from .parsers.html_xliff import HtmlXliffParser


class XliffGenerator(SimplerXMLGenerator):
    def __init__(self, out=None, encoding="iso-8859-1"):
        super().__init__(out, encoding)
        self.unit_id = 1
        self.rich_text_parser = HtmlXliffParser()

    def start_xliff(self, src_language_code, target_language_code):
        self.startDocument()
        self.startElement(
            XliffElements.XLIFF,
            {
                "version": "2.0",
                "xmlns": "urn:oasis:names:tc:xliff:document:2.0",
                "xmlns:slr": "urn:oasis:names:tc:xliff:sizerestriction:2.0",
                "xmlns:mda": "urn:oasis:names:tc:xliff:metadata:2.0",
                "srcLang": src_language_code,
                "trgLang": target_language_code,
            },
        )

    def end_xliff(self):
        self.endElement(XliffElements.XLIFF)
        self.endDocument()

    def start_file(self, attrs):
        self.startElement(XliffElements.FILE, attrs=attrs)

    def start_end_meta(self, categories):
        self.startElement(XliffElements.METADATA, {})
        for category in categories:
            self.startElement(
                XliffElements.METAGROUP,
                {MetaGroupAttributes.CATEGORY: category.get("category")},
            )
            for meta_type, value in category.get("elements"):
                self.startElement(XliffElements.META, {MetaAttributes.TYPE: meta_type})
                self.characters(value)
                self.endElement(XliffElements.META)
            self.endElement(XliffElements.METAGROUP)
        self.endElement(XliffElements.METADATA)

    def end_file(self):
        self.endElement(XliffElements.FILE)
        self.rich_text_parser.reset()

    def start_end_unit(self, attrs, content, page=None, target=None):
        """
        when called with a page parameter, content is treated as a field. When called without
        content is treated as raw data e.g. a block value. Also see start_end_source
        :param attrs: attributes for unit element
        :param content: field/raw_data
        :param page: Page object
        :param target: str value, when serializing non-translatable structures like picker blocks we want to pre-fill
        the target value to the relation stays intact
        """
        self.startElement(XliffElements.UNIT, attrs)
        if page and isinstance(content, RichTextField):
            html_value = content.value_to_string(page)
            self.rich_text_parser.feed(html_value)
        elif isinstance(content, (RichText, SafeText)):
            html_value = str(content)
            self.rich_text_parser.feed(html_value)
        self.start_end_source(content, page, target)
        self.endElement(XliffElements.UNIT)

        if isinstance(content, (RichText, SafeText)):
            self.rich_text_parser.reset()

    def start_group(self, attrs):
        self.startElement(XliffElements.GROUP, attrs=attrs)

    def end_group(self):
        self.endElement(XliffElements.GROUP)

    def start_end_source(self, content, page=None, target=None):
        if isinstance(content, (RichText, SafeText, RichTextField)):
            self.set_richtext_source_data()
            return

        self.startElement(XliffElements.SEGMENT, {})
        if not page:
            self.startElement(XliffElements.SOURCE, {})
            self.characters(str(content))
            self.endElement(XliffElements.SOURCE)
            self.addQuickElement(XliffElements.TARGET, contents=target)
        else:
            self.startElement(XliffElements.SOURCE, {})
            self.characters(content.value_to_string(page))
            self.endElement(XliffElements.SOURCE)
            self.addQuickElement(XliffElements.TARGET, contents=target)
        self.endElement(XliffElements.SEGMENT)

    def set_richtext_source_data(self):
        # First we set the header tag which contains an internal file.
        # This internal file is the richtext converted to base64
        self.startElement(XliffElements.HEADER, {})
        self.startElement(XliffElements.INTERNAL_FILE, {})
        self.characters(self.rich_text_parser.encode_html())
        self.endElement(XliffElements.INTERNAL_FILE)
        self.endElement(XliffElements.HEADER)
        for tag, item in self.rich_text_parser.content_list:
            # For each item in the content list,
            # we create a source tag with the data and an empty target tag used for translation
            self.startElement(XliffElements.SEGMENT, {"tag": tag})
            self.startElement(XliffElements.SOURCE, {})
            item = item.replace("\n", "").strip()
            self.characters(item)
            self.endElement(XliffElements.SOURCE)
            self.addQuickElement(XliffElements.TARGET)
            self.endElement(XliffElements.SEGMENT)
