"""
integration tests are the only tests that make a full roundtrip.
"""

import json

import pytest
from bs4 import BeautifulSoup as bs

from django.core import serializers

from wagtail.core.blocks import StreamValue

from ..utils import get_object_ids


# TODO check if this test is relevant and either rewrite or remove (since it contains a lot of ZG factories)
@pytest.mark.django_db
@pytest.mark.skip(reason="Needs a fix")
def test_stream_data(
    home_en,
    site,
    zg_marketing_page_factory,
    zg_products_page_factory,
    inspiration_detail_page_factory,
    language_factory,
):
    homepage = home_en
    products = zg_products_page_factory(parent=site.root_page)
    marketing_page = zg_marketing_page_factory(
        parent=products,
        title="marketingpage",
        slug="marktingpage_debug",
        description="markting page",
        display_upcoming_events=False,
    )
    case_study_page = inspiration_detail_page_factory()

    # set a streamfield block
    json_data = [
        {
            "type": "case_studies",
            "value": {
                "title": "Lassen Sie sich inspirieren",
                "case_studies": [
                    {
                        "type": "case_study",
                        "value": case_study_page.pk,
                        "id": "e67906ba-a0f5-4eed-907d-08d45b45cefc",
                    }
                ],
            },
            "id": "473511bf-3177-4db0-897e-03220ae54e2c",
        }
    ]
    marketing_page.body = json.dumps(json_data)
    marketing_page.save()
    german_language = language_factory(language_code="de", is_default=False)
    homepage.create_translation(
        german_language, copy_fields=True, parent=homepage.get_parent()
    )
    serialized_page = serializers.serialize(
        "xliff", [marketing_page], target_language=german_language.language_code
    )
    soup = bs(serialized_page, "lxml-xml")
    body_xml_str = f"""
        <group canResegment="no" id="body" name="body" translate="yes" type="local:StreamField">
            <group canResegment="no" id="case_studies_0" name="case_studies" type="local:structural">
                <unit canResegment="no" id="title-0" name="title" translate="yes" type="local:title">
                    <segment>
                        <source>Lassen Sie sich inspirieren</source>
                        <target/>
                    </segment>
                </unit>
                <group canResegment="no" id="case_studies_0" name="case_studies" type="local:stream">
                    <unit canResegment="no" id="case_study-1" name="case_study" translate="no" type="local:case_study">
                        <segment>
                            <source>{case_study_page.pk}</source>
                            <target>{case_study_page.pk}</target>
                        </segment>
                    </unit>
                </group>
            </group>
        </group>"""
    xml_condensed = "".join([line.strip() for line in body_xml_str.split("\n")])
    assert str(soup.find(id="body")) == xml_condensed

    # translate required fields
    soup.find(id="title").find("target").string = "marketingpage-translated"
    soup.find(id="slug").find("target").string = "marketingpage-translated"
    soup.find(id="description").find("target").string = "marketingpage-translated"
    soup.find(id="title-0").find("target").string = "Case studies title translated"

    translated_pages = serializers.deserialize(
        "xliff",
        str(soup),
        object_ids=get_object_ids([marketing_page]),
        create_pages=True,
    ).all()
    translated_page = translated_pages[0]
    # don' assert the ID
    del translated_page.body.stream_data[0]["id"]
    # validate the streamdata
    assert translated_page.body.stream_data == [
        {
            "type": "case_studies",
            "value": {
                "title": "Case studies title translated",
                "case_studies": [{"type": "case_study", "value": case_study_page.pk}],
            },
        }
    ]
    # streamfields with a streamchild can be opened
    assert isinstance(translated_page.body[0], StreamValue.StreamChild)
