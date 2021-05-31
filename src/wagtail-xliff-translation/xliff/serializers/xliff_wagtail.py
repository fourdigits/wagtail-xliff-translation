from xml.dom import pulldom

from wagtailtrans.models import Language, TranslatablePage

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers import base
from django.db import transaction
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from zg.django.website.models import ZGSiteRoot
from zg.django.xliff.constants import (
    FileAttributes,
    MetaAttributes,
    MetaGroupAttributes,
    XliffAttributes,
    XliffElements,
)
from zg.django.xliff.helpers.page import PageHelper
from zg.django.xliff.helpers.Translation import TranslationHelper


class XliffWagtailDeserializer(base.Deserializer):
    def __init__(self, stream_or_string, **options):
        super().__init__(stream_or_string, **options)
        self.event_stream = pulldom.parse(self.stream)
        self.object_ids = self.options.get("object_ids")
        self.parent_page = self.options.get("parent_page")
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
            target_lang_instance = Language.objects.get(code=self.target_lang)
        except ObjectDoesNotExist:
            raise base.DeserializationError(
                _("target language (%s) does not exist" % self.target_lang)
            )
        return page, target_lang_instance

    def get_translation_target_page(self, page, language):
        # Method to determine the translated counterpart.
        page = page.specific
        try:
            translation_target_page = (
                page.get_translations(only_live=False).get(language=language).specific
            )
        except TranslatablePage.DoesNotExist:
            translation_target_page = page.translations.get(language=language)
        return translation_target_page

    def check_page_has_translations(self, page, language):
        if not isinstance(page, TranslatablePage):
            return False
        if (
            page.specific.get_translations(only_live=False)
            .filter(language=language)
            .first()
        ):
            return True
        elif page.specific.translations.filter(language=language).first():
            return True
        return False

    def determine_appropriate_translation_parent(self, page, language):
        """
        Try to determine an appropriate parent for a certain page in a certain language

        Page: The page that is to be translated into argument language

        Raises an error if the parent is an instance of ZGSiteRoot
        """
        if not isinstance(page, TranslatablePage):
            raise base.DeserializationError(
                "Unable to find a decent parent for this page. Please enter a manual parent for this page on the import page"
            )
        parent = page.get_parent().specific
        if self.check_page_has_translations(parent, language):
            intended_translation_parent = self.get_translation_target_page(
                parent, language
            )
        else:
            intended_translation_parent = self.determine_appropriate_translation_parent(
                parent, language
            )
        if isinstance(intended_translation_parent, ZGSiteRoot):
            raise base.DeserializationError(
                "Unable to find a decent parent for this page. Please enter a manual parent for this page on the import page"
            )
        return intended_translation_parent

    def create_translation_and_set_canonical(self, src_page, language, parent):
        translation_target_page = src_page.create_translation(
            language, copy_fields=True, parent=parent
        )
        # We need to set the canonical page here, since the create translation always sets the src_page as canonical,
        # and we want to keep some consistency in canonical pages. If the src_page has no canonical_page and isn't
        # canonical either, the canonical page gets set through the create_translation method above and we don't need
        # to set it manually.
        if src_page.canonical_page or src_page.is_canonical:
            translation_target_page.canonical_page = (
                src_page.canonical_page if not src_page.is_canonical else src_page
            )
        return translation_target_page

    def handle_object(self, file_node, is_translation_child):
        page, target_lang_instance = self.validate_object(file_node)
        translation_helper = TranslationHelper(page)
        src_page, is_canonical = translation_helper.src_page
        if not is_translation_child and self.parent_page:
            # This flow should only be followed once, on the highest file node. It creates a translation of the page
            # underneath the page that has been entered in the upload form (if there is a page)
            parent = self.parent_page
            try:
                translation_target_page = self.create_translation_and_set_canonical(
                    src_page, target_lang_instance, parent
                )
            except Exception:
                translation_target_page = self.get_translation_target_page(
                    src_page, target_lang_instance
                )

                target_page_url = reverse(
                    "wagtailadmin_explore", args=[translation_target_page.pk]
                )
                # Since we can't (and shouldn't) move an existing page, we raise an error and let the editor decide whats next
                raise base.DeserializationError(
                    mark_safe(
                        f"Cannot manually set a parent because the translated version of the <a "
                        f"href={target_page_url}>page</a> already exists.<br/>"
                    )
                )
        # elif not src_page.has_translation(target_lang_instance) and self.create_pages:
        elif (
            not self.check_page_has_translations(src_page, target_lang_instance)
            and self.create_pages
        ):
            # Here, we try to determine a parent page for the new page.
            parent = self.determine_appropriate_translation_parent(
                src_page, target_lang_instance
            )
            # foreign key data is copied 'as is', meaning picker fields (page/image etc) will carry the same content
            # as it's source
            translation_target_page = self.create_translation_and_set_canonical(
                src_page, target_lang_instance, parent
            )
        else:
            translation_target_page = self.get_translation_target_page(
                src_page, target_lang_instance
            )
        return translation_helper.translate_page(file_node, translation_target_page)
