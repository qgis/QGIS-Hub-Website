from base.validator import filesize_validator
from django import forms
from django.utils.translation import gettext_lazy as _
import os


class ResourceBaseReviewForm(forms.Form):
    """Base Review Form for sharing file app."""

    APPROVAL_OPTIONS = [("approve", "Approve"), ("reject", "Reject")]
    approval = forms.ChoiceField(
        required=True,
        choices=APPROVAL_OPTIONS,
        widget=forms.RadioSelect,
        initial="approve",
    )
    comment = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.resource_name = kwargs.pop("resource_name", "resource")
        super(ResourceBaseReviewForm, self).__init__(*args, **kwargs)
        self.fields["comment"].widget = forms.Textarea(
            attrs={
            "placeholder": _(
                "Please provide clear feedback if you decided to not "
                "approve this %s."
            )
            % self.resource_name,
            "rows": "5",
            "class": "textarea",
            }
        )


class ResourceBaseSearchForm(forms.Form):
    """Base Search Form for sharing file app."""

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "search-query", "placeholder": "Search"}
        ),
    )


class ResourceBaseCleanFileForm(object):
    def clean_file(self):
        """
        Cleaning file field data.
        """

        file = self.cleaned_data["file"]
        file_extension = os.path.splitext(file.name)[1]
        is_gpkg = file_extension == ".gpkg"
        is_map = getattr(self, 'is_map', False)
        if filesize_validator(file.file, is_gpkg, is_map):
            return file
