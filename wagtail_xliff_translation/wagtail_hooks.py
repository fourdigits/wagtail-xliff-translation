from django.urls import include, path, reverse
from django.utils.translation import gettext as _

from wagtail.admin import widgets as wagtailadmin_widgets
from wagtail.core import hooks

from .views import DownloadView, UploadView


@hooks.register("register_admin_urls")
def register_admin_urls():
    urls = [
        path("download/page/<int:page_id>/", DownloadView.as_view(), name="download"),
        path("import/page/<int:page_id>/", UploadView.as_view(), name="upload"),
    ]

    return [path("xliff/", include((urls, "xliff"), namespace="xliff"))]


@hooks.register("register_page_listing_more_buttons")
def page_listing_more_buttons(page, page_perms, is_parent=False, next_url=None):
    if page_perms.user.is_superuser and not page.is_root():
        yield wagtailadmin_widgets.Button(
            _("Download XLIFF"), reverse("xliff:download", args=[page.id]), priority=60
        )
        yield wagtailadmin_widgets.Button(
            _("Upload XLIFF"), reverse("xliff:upload", args=[page.id]), priority=61
        )
