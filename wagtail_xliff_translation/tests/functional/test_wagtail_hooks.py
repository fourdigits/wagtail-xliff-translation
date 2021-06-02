import pytest

from django.urls import reverse

@pytest.mark.skip(reason="buttons not in context[36]")
@pytest.mark.django_db
def test_xliff_more_buttons(admin_client, page_factory):
    breakpoint()
    page_factory()
    resp = admin_client.get(reverse("wagtailadmin_explore_root"))
    # assert the last more button is download xliff
    assert set(["Download XLIFF", "Upload XLIFF"]) <= set(
        [button.label for button in resp.context[36].get("buttons")]
    )
