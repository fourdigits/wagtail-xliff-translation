from django.conf import settings
from django.core.serializers import base
from django.core.serializers.base import SerializationError
from django.db.models import BooleanField
from django.utils.translation import ugettext as _

from wagtail.core.blocks import PageChooserBlock, StreamValue, StructValue
from wagtail.core.fields import StreamField
from wagtail.core.models import Locale, Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from ..constants import (
    ContentType,
    FileAttributes,
    GroupAttributes,
    MetaGroupAttributes,
    UnitAttributes,
)
from ..helpers.page import PageHelper
from ..utils import bool_to_xliff
from ..xliff_generator import XliffGenerator


class WagtailXliffSerializer(base.Serializer):
    def __init__(self):
        self.page_helper = PageHelper()
        self.group_id = 0
        self.unit_id = 0

    def serialize(
        self, queryset, *, stream=None, fields=None, **options
    ):  # pragma: no mccabe
        self.options = options
        self.stream = stream if stream is not None else self.stream_class()
        self.selected_fields = fields
        if not self.page_helper.all_translatable_pages(queryset):
            raise base.SerializationError(
                _("all instances must be of type %s" % Page.__name__)
            )
        if not self.page_helper.all_same_src_language(queryset):
            raise base.SerializationError(
                _("all instances must have the same source language")
            )

        self.src_language_code = queryset[0].locale.language_code
        self.target_language_code = self.options["target_language"]

        if not Locale.objects.filter(language_code=self.target_language_code).exists():
            raise base.SerializationError(_("invalid target language"))

        self.start_serialization()
        self.first = True
        for count, obj in enumerate(queryset, start=1):
            self.start_object(obj, queryset)
            for field in obj._meta.fields:
                if field.serialize:
                    if field.remote_field is None:
                        if (
                            self.selected_fields is None
                            or field.attname in self.selected_fields
                        ):
                            self.handle_field(obj, field)
            self.end_object(obj)
            self.first = self.first and False
        self.end_serialization()
        return self.getvalue()

    def start_serialization(self):
        self.xliff = XliffGenerator(
            self.stream, self.options.get("encoding", settings.DEFAULT_CHARSET)
        )
        self.xliff.start_xliff(self.src_language_code, self.target_language_code)

    def end_serialization(self):
        self.xliff.end_xliff()

    def start_object(self, obj, queryset):
        self.page_helper.page = obj
        self.xliff.start_file({FileAttributes.ID: self.page_helper.object_id})
        self.xliff.start_end_meta(
            [
                {
                    MetaGroupAttributes.CATEGORY: "object_nesting",
                    "elements": [
                        (
                            "child",
                            bool_to_xliff(
                                self.page_helper.is_translation_child(queryset)
                            ),
                        )
                    ],
                }
            ]
        )

    def end_object(self, obj):
        self.xliff.end_file()

    def handle_field(self, obj, field):
        if self.page_helper.verify_include_in_export(field):
            if isinstance(field, StreamField):
                self.handle_streamfield(obj, field)
            else:
                target = None
                attrs = {
                    UnitAttributes.ID: field.name,
                    UnitAttributes.TYPE: "local:" + field.__class__.__name__,
                    UnitAttributes.NAME: field.name,
                    UnitAttributes.TRANSLATE: bool_to_xliff(
                        self.page_helper.verify_translatable(field)
                    ),
                    UnitAttributes.CAN_RESEGMENT: "no",
                }
                if hasattr(field, "max_length") and field.max_length:
                    attrs[UnitAttributes.SIZE_RESTRICTION] = str(field.max_length)
                if isinstance(field, BooleanField):
                    target = str(field.value_from_object(obj))
                self.xliff.start_end_unit(attrs, field, page=obj, target=target)

    def handle_streamfield(self, obj, field):
        attrs = {
            GroupAttributes.ID: field.name,
            GroupAttributes.TYPE: "local:" + field.__class__.__name__,
            GroupAttributes.NAME: field.name,
            GroupAttributes.TRANSLATE: bool_to_xliff(
                self.page_helper.verify_translatable(field)
            ),
            UnitAttributes.CAN_RESEGMENT: "no",
        }
        self.xliff.start_group(attrs)
        for block in field.value_from_object(obj):
            self.handle_block(block)
        self.xliff.end_group()

    def handle_block(self, block):
        if isinstance(block.value, (StreamValue, list)):
            self.handle_structural_block(
                block.value, block.block.name, ContentType.STREAM
            )
        elif isinstance(block.value, StructValue):
            self.handle_structural_block(
                block.value, block.block.name, ContentType.STRUCTURAL
            )
        else:
            self.handle_regular_block(block.value, block.block.name, block.block)

    def handle_regular_block(
        self, block_value, block_name, block_type, flat=False, can_resegment=False
    ):
        target_value = ""
        attrs = {
            UnitAttributes.ID: f"{block_name}-{self.unit_id}",
            UnitAttributes.TYPE: ContentType.FLAT if flat else f"local:{block_name}",
            UnitAttributes.NAME: block_name,
            UnitAttributes.TRANSLATE: bool_to_xliff(
                self.page_helper.verify_translatable_block(block_type) or flat
            ),
            UnitAttributes.CAN_RESEGMENT: bool_to_xliff(can_resegment),
        }
        if not self.page_helper.verify_translatable_block(block_type):
            if isinstance(
                block_type,
                (
                    ImageChooserBlock,
                    PageChooserBlock,
                    DocumentChooserBlock,
                ),
            ):
                if block_value:
                    block_value = str(block_value.id)
                    target_value = block_value
            elif isinstance(block_type, SnippetChooserBlock):
                # Snippets are out of scope for this project
                if block_name.startswith("mounting_type"):
                    block_value = str(block_value.id)
                    target_value = block_value
            elif block_value:
                block_value = str(block_value)
                target_value = block_value
        try:
            self.xliff.start_end_unit(attrs, block_value, target=target_value)
        except Exception as err:
            raise SerializationError(
                _("unserializable block type: %s (%s)" % (block_name, err))
            )
        finally:
            self.unit_id += 1

    def handle_structural_block(
        self, block_value, block_name, block_type, can_resegment=False
    ):
        attrs = {
            GroupAttributes.ID: f"{block_name}_{self.group_id}",
            GroupAttributes.TYPE: block_type,
            GroupAttributes.NAME: block_name,
            GroupAttributes.CAN_RESEGMENT: bool_to_xliff(can_resegment),
        }
        self.xliff.start_group(attrs)
        if isinstance(block_value, StructValue):
            for field in block_value:
                field_value = block_value.get(field)
                if isinstance(field_value, StreamValue):
                    self.handle_structural_block(field_value, field, ContentType.STREAM)
                elif isinstance(field_value, (StructValue, list)):
                    self.handle_structural_block(
                        field_value, field, ContentType.STRUCTURAL_FLAT
                    )
                else:
                    self.handle_regular_block(
                        field_value, field, block_value.bound_blocks[field].block
                    )
        elif isinstance(block_value, (StreamValue, list)):
            for field in block_value:
                if isinstance(field, (list, StreamValue.StreamChild)):
                    self.handle_block(field)
                elif isinstance(field, StructValue):
                    self.handle_structural_block(
                        field, ContentType.STRUCTURAL_FLAT, ContentType.STRUCTURAL_FLAT
                    )
                else:
                    self.handle_regular_block(
                        field, f"{block_name}-item", block_name, flat=True
                    )
        self.xliff.end_group()
        self.group_id += 1
