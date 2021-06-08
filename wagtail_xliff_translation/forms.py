from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext as _n

from wagtail.core.models import Locale


class DownloadForm(forms.Form):
    language = forms.ModelChoiceField(
        label=_("Target locale"), queryset=Locale.objects.all()
    )
    include_subtree = forms.BooleanField(
        required=False,
        help_text=_("All pages in the subtree will be added to the XLIFF."),
        initial=True,
    )

    def __init__(self, instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["language"].queryset = Locale.objects.exclude(
            language_code=instance.locale.language_code
        )

        hide_include_subtree = True
        descendant_count = instance.get_descendants().count()

        if descendant_count > 0:
            hide_include_subtree = False
            self.fields["include_subtree"].label = _n(
                "Include subtree ({} page)",
                "Include subtree ({} pages)",
                descendant_count,
            ).format(descendant_count)

        if hide_include_subtree:
            self.fields["include_subtree"].widget = forms.HiddenInput()


class ImportForm(forms.Form):
    xliff = forms.FileField(label=_("XLIFF file"))
    update_target_page = forms.BooleanField(
        initial=True,
        required=False,
        help_text=mark_safe(
            _(
                "On: the target page will be updated.<br>"
                "Off: the target page will be skipped."
            )
        ),
    )
    update_subtree = forms.BooleanField(
        initial=True,
        required=False,
        help_text=mark_safe(
            _(
                "On: the subtree will be updated.<br>"
                "Off: the subtree will be skipped."
            )
        ),
    )
    create_pages = forms.BooleanField(
        initial=True,
        required=False,
        help_text=mark_safe(
            _(
                "On: the pages in the target language will be created if they do not exist.<br>"
                "Off: the pages in the target language will be skipped if they do not exist."
            )
        ),
    )

    def clean(self):
        data = super().clean()
        update_target_page = data["update_target_page"]
        update_subtree = data["update_subtree"]
        if not update_target_page and not update_subtree:
            msg = _(
                "No pages to import. Select one of 'Update target page' or 'Update subtree' or both."
            )
            self.add_error("update_target_page", msg)
            self.add_error("update_subtree", msg)

        return data
