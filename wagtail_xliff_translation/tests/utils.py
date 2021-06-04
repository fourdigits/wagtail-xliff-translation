import os
import re
from xml.dom.minidom import parseString

from django.conf import settings

from wagtail_xliff_translation.constants import FileAttributes, XliffElements
from wagtail_xliff_translation.helpers.page import PageHelper


def get_sample_data(file):
    path = os.path.join(settings.BASE_DIR, "test_app/data/", file)
    with open(path, "r") as file_data:
        return file_data.read()


def get_object_ids(pages):
    return [PageHelper.get_object_id(page) for page in pages]


def set_file_ids(data, object_ids):
    xml = parseString(data)
    # add the object_ids of the pages we are testing against, note that the object id list
    # must mirror the sample data!
    for file_node, object_id in zip(
        xml.getElementsByTagName(XliffElements.FILE), object_ids
    ):
        file_node.setAttribute(FileAttributes.ID, object_id)
    return xml.toxml()


def get_condensed_sample_data(file, pages):
    data = get_sample_data(file)
    with_ids = set_file_ids(data, pages)
    return "".join([line.strip() for line in with_ids.split("\n")])


def i_compare_string(string_one, string_two):
    """compare strings ignoring whitespaces/ new lines and tabs
    this allows us to keep the sample data in readable format and keeping the exported data condensed
    """
    return re.sub(r"\s+", "", string_one) == re.sub(r"\s+", "", string_two)


def sample_data_equals(data, file):
    with_pk = parseString(data)
    # pk will be different on each run, don't assert it
    for file_node in with_pk.getElementsByTagName(XliffElements.FILE):
        file_node.removeAttribute(FileAttributes.ID)
    without_pk = with_pk.toxml()
    file_data = get_sample_data(file)
    return i_compare_string(without_pk, file_data)
