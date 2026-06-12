from base.forms.processing_forms import ResourceBaseCleanFileForm
from django import forms
from django.utils.translation import gettext_lazy as _
from processing_scripts.models import ProcessingScript, PyQtVersion
from processing_scripts.validator import processing_script_validator
from taggit.forms import TagField


class PyQtVersionMultiSelectWidget(forms.CheckboxSelectMultiple):
    """Custom multiselect widget for PyQt versions with enhanced styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({"class": "pyqt-versions-checkboxes"})


class ResourceFormMixin(forms.ModelForm):
    tags = TagField(required=False)
    pyqt_versions = forms.ModelMultipleChoiceField(
        queryset=PyQtVersion.objects.all().order_by("order", "name"),
        required=False,
        widget=PyQtVersionMultiSelectWidget(),
        label=_("PyQt Versions"),
        help_text=_("Select the PyQt versions this script is compatible with"),
    )

    class Meta:
        model = ProcessingScript
        fields = [
            "file",
            "thumbnail_image",
            "name",
            "description",
            "tags",
            "dependencies",
            "pyqt_versions",
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""

    def clean_file(self):
        """
        Cleaning file field data.
        """
        script_file = super(UploadForm, self).clean_file()
        is_valid = processing_script_validator(script_file.file)
        if not is_valid:
            raise forms.ValidationError(
                _("Invalid script file. Please ensure your file is correct.")
            )
        return script_file


class UpdateForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Script Update Form."""

    def clean_file(self):
        """
        Cleaning file field data.
        """
        script_file = super(UpdateForm, self).clean_file()
        is_valid = processing_script_validator(script_file.file)
        if not is_valid:
            raise forms.ValidationError(
                _("Invalid script file. Please ensure your file is correct.")
            )
        return script_file
