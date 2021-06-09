from xml.dom import pulldom

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.serializers import base
from django.db import transaction
from django.utils.translation import ugettext as _

from wagtail.core.models import Locale, ParentNotTranslatedError

from ..constants import (
    FileAttributes,
    MetaAttributes,
    MetaGroupAttributes,
    XliffAttributes,
    XliffElements,
)
from ..helpers.page import PageHelper
from ..helpers.Translation import TranslationHelper


class XliffWagtailDeserializer(base.Deserializer):
    def __init__(self, stream_or_string, **options):
        super().__init__(stream_or_string, **options)
        self.event_stream = pulldom.parse(self.stream)
        self.object_ids = self.options.get("object_ids")
        self.create_pages = self.options.get("create_pages")

    def __next__(self):
        for event, node in self.event_stream:
            if event == pulldom.START_ELEMENT and node.nodeName == XliffElements.XLIFF:
                self.src_lang = node.getAttribute(XliffAttributes.SRCLANG)
                self.target_lang = node.getAttribute(XliffAttributes.TRGLANG)
                self.event_stream.expandNode(node)
                objects = []
                with transaction.atomic():
                    for file_node in node.getElementsByTagName(XliffElements.FILE):
                        if file_node.getAttribute(FileAttributes.ID) in self.object_ids:
                            meta_info = self.get_meta_information(file_node)
                            objects.append(
                                self.handle_object(
                                    file_node,
                                    PageHelper.verify_translation_child(meta_info),
                                )
                            )

                return objects
        raise StopIteration

    def all(self):
        return [result for result in self][0]

    def get_meta_information(self, file_node):
        meta_data = []
        meta_data_xml = file_node.getElementsByTagName(XliffElements.METADATA)[0]
        for meta_group in meta_data_xml.getElementsByTagName(XliffElements.METAGROUP):
            data = {
                "category": meta_group.getAttribute(MetaGroupAttributes.CATEGORY),
                "elements": [],
            }
            for data_element in meta_group.getElementsByTagName(XliffElements.META):
                data["elements"].append(
                    (
                        data_element.getAttribute(MetaAttributes.TYPE),
                        data_element.firstChild.wholeText,
                    )
                )
            meta_data.append(data)
        return meta_data

    def validate_object(self, file_node):
        """
        Try and get the page object from the filenode. The page object is the page that is about to be translated into
        the target language defined in the file node. This method also obtains the language instance and returns both
        """
        try:
            page = PageHelper.get_instance_from_node(file_node)
        except ObjectDoesNotExist:
            raise base.DeserializationError(
                _(
                    "failed to retrieve src page %s"
                    % file_node.getAttribute(FileAttributes.ID)
                )
            )
        try:
            target_lang_instance = Locale.objects.get(language_code=self.target_lang)
        except ObjectDoesNotExist:
            raise base.DeserializationError(
                _("target language (%s) does not exist" % self.target_lang)
            )
        return page, target_lang_instance

    def handle_object(self, file_node, is_translation_child):
        """
        Here we translate a page to the target locale. If the page already exists, we use
        that page to create the translation. If the parent of the source page is not yet
        translated, we throw an error because the tree needs to be identical until said parent.
        """
        src_page, locale = self.validate_object(file_node)
        translation_helper = TranslationHelper(src_page)
        try:
            translation_target_page = src_page.copy_for_translation(
                locale, copy_parents=False, alias=False, exclude_fields=None
            )
        except ParentNotTranslatedError:
            raise base.DeserializationError(
                f"To translate '{src_page}' it is required that the parent "
                f"of '{src_page}' is also translated in the target locale: '{locale}'"
            )
        except ValidationError as e:
            if (
                "Page with this Translation key and Locale already exists."
                in e.messages
            ):
                translation_target_page = src_page.get_translation(locale)
            else:
                raise base.DeserializationError(e.messages)
        return translation_helper.translate_page(file_node, translation_target_page)
