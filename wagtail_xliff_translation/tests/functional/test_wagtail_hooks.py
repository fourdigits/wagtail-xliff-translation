import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_xliff_more_buttons(admin_client, page):
    resp = admin_client.get(reverse("wagtailadmin_explore_root"))
    # assert the last more button is download xliff
    assert set(["Download XLIFF", "Upload XLIFF"]) <= set(
        [button.label for button in resp.context[63].get("buttons")]
    )
