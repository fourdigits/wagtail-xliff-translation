from treebeard.mp_tree import MP_Node

from django.apps import apps
from django.db.models import fields

from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page

from ..constants import FileAttributes, MetaGroupAttributes
from ..utils import xliff_to_bool


class PageHelper:
    def __init__(self, page=None):
        self.page = page

    @classmethod
    def get_object_id(cls, obj):
        return "_".join([str(obj.pk), obj._meta.app_label, obj._meta.model_name])

    @property
    def object_id(self):
        return self.get_object_id(self.page)

    @staticmethod
    def get_instance_from_node(file_node):
        # Get the page that is to be translated
        xliff_id = file_node.getAttribute(FileAttributes.ID)
        temp = xliff_id.split("_")
        pk = temp[0]
        # strip the first and last item.
        app_label = "_".join(temp[1:-1])
        model_str = temp[-1]
        Model = apps.get_model(app_label=app_label, model_name=model_str)
        return Model.objects.get(pk=pk)

    @staticmethod
    def all_translatable_pages(queryset):
        return all(isinstance(obj, Page) for obj in queryset)

    @staticmethod
    def all_same_src_language(queryset):
        return all(obj.locale_id == queryset[0].locale_id for obj in queryset)

    def is_translation_child(self, queryset):
        return self.page.get_parent().specific in queryset

    @staticmethod
    def verify_translation_child(meta_info):
        object_nesting_meta = [
            object_nesting_meta
            for object_nesting_meta in meta_info
            if object_nesting_meta[MetaGroupAttributes.CATEGORY] == "object_nesting"
        ][0]
        return xliff_to_bool(object_nesting_meta["elements"][0][1])

    def verify_include_in_export(self, field):
        model = type(self.page)
        return (
            # return fields with value
            field.value_to_string(self.page)
            # ignore fields with factory generated 'none's'
            and field.value_to_string(self.page) != "None"
            # Ignore non-editable fields
            and field.editable
            # Ignore fields defined by MP_Node mixin
            and not (
                issubclass(model, MP_Node)
                and field.name in ["path", "depth", "numchild"]
            )
            # Ignore some editable fields defined on Page
            and not (
                issubclass(model, Page)
                and field.name
                in [
                    "show_in_menus",
                    "go_live_at",
                    "expire_at",
                    "first_published_at",
                    "content_type",
                    "owner",
                ]
            )
            # ignore zgpage specific fields
            # TODO remove if possible
            and not (
                field.name
                in [
                    "custom_sitemap_change_frequency",
                    "custom_sitemap_priority",
                    "show_sitemap_on_robots",
                ]
            )
        )

    def verify_translatable(self, field):
        must_translate = isinstance(
            field,
            (
                fields.CharField,
                fields.TextField,
                fields.EmailField,
                fields.SlugField,
                fields.URLField,
                RichTextField,
                StreamField,
            ),
        )
        optional_translate = False
        if hasattr(self.page, "translatable_fields"):
            optional_translate = field.__name__ in self.page.translatable_fields
        return must_translate or optional_translate

    def verify_translatable_block(self, block_type):
        must_translate = isinstance(
            block_type,
            (
                blocks.CharBlock,
                blocks.TextBlock,
                blocks.EmailBlock,
                blocks.URLBlock,
                blocks.RichTextBlock,
                blocks.RawHTMLBlock,
                blocks.BlockQuoteBlock,
                blocks.ChoiceBlock,
            ),
        )
        optional_translate = False
        if hasattr(block_type, "translate"):
            optional_translate = block_type.translate
        return must_translate or optional_translate
