from test_app.apps import TestAppConfig


def test_xliff_config():
    assert TestAppConfig.name == "test_app"
