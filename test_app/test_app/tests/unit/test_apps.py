from ...apps import XliffConfig
from ...apps import XliffTestAppConfig

def test_xliff_config():
    assert XliffConfig.name == "xliff"
    assert XliffConfig.label == "xliff"


def test_xliff_test_config():
    assert XliffTestAppConfig.label == "xliff_test"
    assert XliffTestAppConfig.name == "xliff.test"
    assert XliffTestAppConfig.verbose_name == "Xliff import/export testapp"
