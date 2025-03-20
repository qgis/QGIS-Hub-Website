from base.forms.processing_forms import ResourceBaseCleanFileForm
from django import forms
from processing_scripts.models import ProcessingScript
from taggit.forms import TagField
from processing_scripts.validator import processing_script_validator
from django.utils.translation import gettext_lazy as _

class ResourceFormMixin(forms.ModelForm):
    tags = TagField(required=False)
    class Meta:
        model = ProcessingScript
        fields = [
            "file",
            "thumbnail_image",
            "name",
            "description",
            "tags",
            "dependencies"
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""
    
    def clean_file(self):
        """
        Cleaning file field data.
        """
        script_file = self.cleaned_data["file"]
        is_valid = processing_script_validator(script_file.file)
        if not is_valid:
            raise forms.ValidationError(
                _("Invalid script file. Please ensure your file is correct.")
            )
        return script_file


class UpdateForm(ResourceFormMixin):
    """Script Update Form."""
