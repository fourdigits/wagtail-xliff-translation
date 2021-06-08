from django.urls import include, path, reverse
from django.utils.translation import gettext as _

from wagtail.admin import widgets as wagtailadmin_widgets
from wagtail.core import hooks

from .views import DownloadView, UploadView


@hooks.register("register_admin_urls")
def register_admin_urls():
    urls = [
        path("<int:page_id>/xliff/download/", DownloadView.as_view(), name="download"),
        path("<int:page_id>/xliff/upload/", UploadView.as_view(), name="upload"),
    ]

    return [path("pages/", include((urls, "xliff"), namespace="xliff"))]


@hooks.register("register_page_listing_more_buttons")
def page_listing_more_buttons(page, page_perms, is_parent=False, next_url=None):
    if page_perms.user.is_superuser and not page.is_root():
        yield wagtailadmin_widgets.Button(
            _("Download XLIFF"), reverse("xliff:download", args=[page.id]), priority=61
        )
        yield wagtailadmin_widgets.Button(
            _("Upload XLIFF"), reverse("xliff:upload", args=[page.id]), priority=62
        )
