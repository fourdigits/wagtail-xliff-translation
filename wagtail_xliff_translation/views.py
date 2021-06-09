from django.contrib import messages
from django.core import serializers
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.serializers.base import DeserializationError, SerializationError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin

from wagtail.core.models import Page

from wagtail_xliff_translation.forms import DownloadForm, ImportForm

from .helpers import PageHelper


class BaseView(SingleObjectMixin, TemplateView):
    def get_title(self):
        return self.title

    def get_subtitle(self):
        return f"#{self.object.id} " + self.object.get_admin_display_title()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"form": self.get_form()})
        return context

    def get_object(self, **kwargs):
        page = get_object_or_404(Page, id=self.kwargs["page_id"]).specific
        # Root has no locale, and isn't translatable.
        if page.is_root() or not hasattr(page, "locale"):
            raise Http404
        return page

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied

        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)


class DownloadView(BaseView):
    title = _("Download XLIFF")
    template_name = "xliff/admin/download.html"

    def get_form(self):
        if self.request.method == "POST":
            return DownloadForm(self.object, self.request.POST)
        else:
            return DownloadForm(self.object)

    def get_success_message(self):
        return _("Download successful")

    def post(self, request, **kwargs):
        form = self.get_form()
        if form.is_valid():
            locale = form.cleaned_data["language"]
            include_subtree = form.cleaned_data["include_subtree"]

            objects = [self.object]
            if include_subtree:
                for obj in self.object.get_descendants():
                    objects.append(obj.specific)
            try:
                data = serializers.serialize(
                    "xliff", objects, target_language=locale.language_code
                )
            except SerializationError as err:
                messages.error(request, str(err))
                context = self.get_context_data(**kwargs)
                return self.render_to_response(context)

            timestamp = timezone.now().strftime("%Y%m%d-%H%M")
            filename = (
                f"{self.object.locale.language_code.upper()}"
                f"2{locale.language_code.upper()}"
                f"-{str(self.object.id)}-{timestamp}.xliff"
            )
            response = HttpResponse(data, content_type="application/x-xliff+xml")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            messages.success(request, self.get_success_message())
            return response

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class UploadView(BaseView):
    title = _("Upload XLIFF")
    template_name = "xliff/admin/import.html"

    def get_form(self):
        if self.request.method == "POST":
            return ImportForm(self.request.POST, self.request.FILES)
        else:
            return ImportForm()

    def get_success_url(self):
        return reverse("wagtailadmin_explore", args=[self.get_object().id])

    def get_success_message(self):
        return _("Upload successful")

    def post(self, request, **kwargs):
        form = self.get_form()
        if form.is_valid():
            data = form.cleaned_data
            xliff = data["xliff"]
            update_target_page = form.cleaned_data["update_target_page"]
            update_subtree = form.cleaned_data["update_subtree"]
            create_pages = form.cleaned_data["create_pages"]

            objects = []
            if update_target_page:
                objects.append(self.object.specific)

            if update_subtree:
                for obj in self.object.get_descendants():
                    objects.append(obj.specific)

            # Create id's.
            object_ids = [PageHelper.get_object_id(obj) for obj in objects]

            try:
                result = serializers.deserialize(
                    "xliff",
                    xliff,
                    object_ids=object_ids,
                    create_pages=create_pages,
                ).all()
                if not result:
                    descendant_ids = [
                        x.id
                        for x in self.object.get_descendants()
                        if self.object.get_descendants()
                    ]
                    # Result being empty here means none of the one or more id's obtained from the XLIFF file tag(s)
                    # have been matched with the target page or the pages in the subtree so no results are returned.
                    # This is most likely due to the fact the user tries to upload an XLIFF file at the wrong page.
                    raise DeserializationError(
                        _(
                            "None of the file objects in the XLIFF file could be matched against "
                            "page id {obj_id} or any of the child pages {desc_ids}. "
                            "Please make sure to upload the proper XLIFF file."
                        ).format(obj_id=self.object.id, desc_ids=descendant_ids)
                    )
            except (ValidationError, DeserializationError) as err:
                messages.error(self.request, str(err))
                context = self.get_context_data(**kwargs)
                return self.render_to_response(context)

            messages.success(self.request, self.get_success_message())
            return redirect(self.get_success_url())

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
