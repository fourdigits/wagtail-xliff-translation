from zg.django.xliff.apps import XliffConfig
from zg.django.xliff.test.apps import XliffTestAppConfig


def test_xliff_config():
    assert XliffConfig.name == "zg.django.xliff"
    assert XliffConfig.label == "xliff"


def test_xliff_test_config():
    assert XliffTestAppConfig.label == "xliff_test"
    assert XliffTestAppConfig.name == "zg.django.xliff.test"
    assert XliffTestAppConfig.verbose_name == "Xliff import/export testapp"
