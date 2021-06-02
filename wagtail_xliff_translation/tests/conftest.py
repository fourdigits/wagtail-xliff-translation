# from .fixtures import *  # noqa
from pytest_factoryboy import register
from test_app.factories import PageFactory, PageWithRichTextFactory, PageWithRichTextFactory, LanguageFactory


register(PageFactory)
register(PageWithRichTextFactory)
register(PageWithRichTextFactory)
register(LanguageFactory)
# @pytest.fixture
# def homepage(db):
#     return Page.get_first_root_node().get_children().first()
