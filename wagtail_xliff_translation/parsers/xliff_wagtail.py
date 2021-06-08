from base64 import b64decode
from html import unescape
from xml.dom.minidom import Element, Text

from wagtail.core.fields import RichTextField

from ..constants import (
    ContentType,
    GroupAttributes,
    PcAttributes,
    PhAttributes,
    UnitAttributes,
    XliffElements,
)
from ..utils import xliff_to_bool


class XliffWagtailParser:
    def __init__(self, file_node):
        self.file_node = file_node

    def get_local_fields(self):
        local_fields = []
        for child in self.file_node.childNodes:
            if child.nodeName == XliffElements.UNIT:
                segment = child.getElementsByTagName(XliffElements.SEGMENT)[0]
                translations = {XliffElements.SOURCE: "", XliffElements.TARGET: ""}
                if xliff_to_bool(child.getAttribute(UnitAttributes.TRANSLATE)):
                    if child.getAttribute(UnitAttributes.TYPE) in (
                        RichTextField.__name__,
                        ContentType.RICHTEXTFIELD,
                    ):
                        translations = self.process_rich_text(child)
                    else:
                        source_data = segment.getElementsByTagName(
                            XliffElements.SOURCE
                        )[0]
                        target_data = segment.getElementsByTagName(
                            XliffElements.TARGET
                        )[0]
                        translations[XliffElements.SOURCE] = source_data.toxml()
                        for text_node in target_data.childNodes:
                            translations[XliffElements.TARGET] += text_node.nodeValue
                elif not xliff_to_bool(child.getAttribute(UnitAttributes.TRANSLATE)):
                    # If not translated, we set the source value as the target value.
                    source_data = segment.getElementsByTagName(XliffElements.SOURCE)[0]
                    translations[XliffElements.SOURCE] = source_data.toxml()
                    for text_node in source_data.childNodes:
                        translations[XliffElements.TARGET] += text_node.nodeValue
                local_fields.append(
                    {
                        "name": child.getAttribute("name"),
                        "source": translations[XliffElements.SOURCE],
                        "target": translations[XliffElements.TARGET],
                    }
                )
        return local_fields

    def _extract_text(self, element):
        """
        Extracts text from an element
        """
        text = ""
        for child in element.childNodes:
            if isinstance(child, Text):
                text += child.data
            elif isinstance(child, Element):
                text += unescape(child.firstChild.data)
        return text

    def _fill_html_from_tags(self, tags_list, html_str):
        for index, target in enumerate(tags_list):
            text = self._extract_text(target)
            html_str = html_str.replace(
                "{{{}}}".format("placeholder_" + str(index)), text
            )
        return html_str

    def process_rich_text(self, file):
        """
        In this method, the richtext part of an xliff file is converted back to flat
        html. The b64 encoded string is used to generate flat HTML containing placeholders.
        After that, we generate two lists containing the old data and the translated data
        and fill the html with said data.
        """
        header_file = file.getElementsByTagName("internal_file")[0]
        html_str = b64decode(header_file.firstChild.data.encode("ascii")).decode(
            "utf-8"
        )
        sources = file.getElementsByTagName("source")
        source_html_str = self._fill_html_from_tags(sources, html_str)
        targets = file.getElementsByTagName("target")
        target_html_str = self._fill_html_from_tags(targets, html_str)
        return {
            XliffElements.SOURCE: source_html_str,
            XliffElements.TARGET: target_html_str,
        }

    def process_child_nodes(self, child_nodes, original_data, streamfield_content):
        html = ""
        rich_text_div = '<div class="rich-text">'
        for child in child_nodes:
            if child.nodeName == XliffElements.PC:
                data_ref_start = original_data[
                    child.getAttribute(PcAttributes.DATAREFSTART)
                ]
                data_ref_end = original_data[
                    child.getAttribute(PcAttributes.DATAREFEND)
                ]
                if not (streamfield_content and data_ref_start == rich_text_div):
                    html += data_ref_start
                html += self.process_child_nodes(child.childNodes, original_data, False)
                if not (streamfield_content and data_ref_start == rich_text_div):
                    html += data_ref_end
            if child.nodeName == XliffElements.TEXT:
                html += child.wholeText
            if child.nodeName == XliffElements.PH:
                html += original_data[child.getAttribute(PhAttributes.DATAREF)]
        return html

    def get_stream_fields(self):
        stream_fields = {}
        # the first 'layer' of groups always refers to to a streamfield
        for stream_field_node in [
            child
            for child in self.file_node.childNodes
            if child.nodeName == XliffElements.GROUP
        ]:
            stream_field = stream_fields[
                stream_field_node.getAttribute(GroupAttributes.NAME)
            ] = []
            for block_node in stream_field_node.childNodes:
                if block_node.nodeName == XliffElements.UNIT:
                    value = self.handle_regular_block(block_node)
                    if value:
                        stream_field.append(value)
                elif block_node.nodeName == XliffElements.GROUP:
                    value = self.handle_structural_block(block_node, top_level=True)
                    if value:
                        stream_field.append(value)
        return stream_fields

    @staticmethod
    def get_target_text_value(block_node):
        text = ""
        text_nodes = block_node.getElementsByTagName(XliffElements.TARGET)[0].childNodes
        for text_node in text_nodes:
            text += text_node.wholeText
        if text.isnumeric():
            text = int(text)
        if text in ("True", "False"):
            if text == "True":
                text = True
            else:
                text = False
        return text

    def handle_regular_block(self, block_node):
        block_name = block_node.getAttribute(UnitAttributes.NAME)
        if block_node.getElementsByTagName(XliffElements.HEADER):
            translations = self.process_rich_text(block_node)
            value = translations.get("target")
        else:
            value = self.get_target_text_value(block_node)
        if value:
            try:
                return {"type": block_name, "value": int(value)}
            except ValueError:
                if value == "True":
                    return {"type": block_name, "value": True}
                elif value == "False":
                    return {"type": block_name, "value": False}
                else:
                    return {"type": block_name, "value": value}
        return None

    def handle_structural_flat_block(self, block):
        structural_flat_block = {}
        structural_list_block = []
        child_nodes = self._remove_text_nodes_from_nodelist(block.childNodes)
        for field in child_nodes:
            field_name = field.getAttribute(UnitAttributes.NAME)
            if field.nodeName == XliffElements.UNIT:
                if block.getElementsByTagName(XliffElements.HEADER):
                    translations = self.process_rich_text(field)
                    target = translations.get("target")
                    if target:
                        structural_flat_block[field_name] = target
                else:
                    text = self.get_target_text_value(field)
                    if text:
                        if field.getAttribute(GroupAttributes.TYPE) == ContentType.FLAT:
                            structural_list_block.append(text)
                        else:
                            structural_flat_block[field_name] = text
            elif block.nodeName == XliffElements.GROUP:
                structural_flat_block[field_name] = self.handle_structural_block(field)
        return structural_flat_block if structural_flat_block else structural_list_block

    def handle_structural_block(self, block_node, top_level=False):  # noqa: C901
        group_type = block_node.getAttribute(GroupAttributes.TYPE)
        group_name = block_node.getAttribute(GroupAttributes.NAME)
        if block_node.nodeName == XliffElements.TEXT:
            return
        elif group_type == ContentType.STREAM:
            if top_level:
                block = self.handle_top_level_stream(block_node, group_name)
                block["value"] = list(filter(None, block["value"]))
            else:
                block = self.handle_nested_stream(block_node)
                block = list(filter(None, block))

        elif group_type == ContentType.STRUCTURAL:
            block = {"type": group_name, "value": {}}
            for child in block_node.childNodes:
                if child.nodeName == XliffElements.UNIT:
                    name = child.getAttribute(UnitAttributes.NAME)
                    if child.getElementsByTagName(XliffElements.HEADER):
                        translations = self.process_rich_text(child)
                        target = translations.get("target")
                        if target:
                            block["value"][name] = target
                    else:
                        text = self.get_target_text_value(child)
                        if text:
                            block["value"][name] = text
                elif child.nodeName == XliffElements.GROUP:
                    name = child.getAttribute(GroupAttributes.NAME)
                    block["value"][name] = self.handle_structural_block(child)
        elif group_type == ContentType.STRUCTURAL_FLAT:
            block = self.handle_structural_flat_block(block_node)
        else:
            return self.handle_regular_block(block_node)
        return block

    def handle_nested_stream(self, block_node):
        block = []
        child_nodes = self._remove_text_nodes_from_nodelist(block_node.childNodes)
        for child in child_nodes:
            if child.getAttribute(UnitAttributes.TYPE) == ContentType.FLAT:
                text = self.get_target_text_value(child)
                if not text:
                    continue
                block.append(text)
            elif child.getAttribute(UnitAttributes.TYPE) == ContentType.STRUCTURAL_FLAT:
                block.append(self.handle_structural_block(child))
            elif child.getAttribute(GroupAttributes.TYPE) == ContentType.STREAM:
                child_block = []
                for grandchild in child.childNodes:
                    child_block.append(self.handle_structural_block(grandchild))
                block.append(child_block)
            elif child.getAttribute(GroupAttributes.TYPE) == ContentType.STRUCTURAL:
                child_block = self.handle_structural_block(child)
                block.append(child_block)
            else:
                child_block = self.handle_regular_block(child)
                block.append(child_block)
        return block

    def handle_top_level_stream(self, block_node, group_name):
        block = {"type": group_name, "value": []}
        child_nodes = self._remove_text_nodes_from_nodelist(block_node.childNodes)
        for child in child_nodes:
            if child.getAttribute(UnitAttributes.TYPE) == ContentType.FLAT:
                text = self.get_target_text_value(child)
                if not text:
                    continue
                block["value"].append(text)
            elif child.getAttribute(UnitAttributes.TYPE) == ContentType.STRUCTURAL_FLAT:
                block["value"].append(self.handle_structural_block(child))
            elif child.getAttribute(GroupAttributes.TYPE) == ContentType.STREAM:
                child_block = {
                    "type": child.getAttribute(UnitAttributes.NAME),
                    "value": [],
                }
                grandchild_nodes = self._remove_text_nodes_from_nodelist(
                    child.childNodes
                )
                for grandchild in grandchild_nodes:
                    child_block["value"].append(
                        self.handle_structural_block(grandchild)
                    )
                block["value"].append(child_block)
            elif child.getAttribute(GroupAttributes.TYPE) == ContentType.STRUCTURAL:
                child_block = self.handle_structural_block(child)
                block["value"].append(child_block)
            else:
                child_block = self.handle_regular_block(child)
                block["value"].append(child_block)
        return block

    def _remove_text_nodes_from_nodelist(self, nodelist):
        return_list = []
        for node in nodelist:
            if not node.nodeName == XliffElements.TEXT:
                return_list.append(node)
        return return_list
