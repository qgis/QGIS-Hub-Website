from base.forms.processing_forms import ResourceBaseCleanFileForm
from django import forms
from screenshots.models import Screenshot
from taggit.forms import TagField


class ResourceFormMixin(forms.ModelForm):
    tags = TagField(required=False)
    is_screenshot = True
    class Meta:
        model = Screenshot
        fields = [
            "file",
            "name",
            "description",
            "tags"
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""


class UpdateForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Screenshot Update Form."""
