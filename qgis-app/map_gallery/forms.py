from base.forms.processing_forms import ResourceBaseCleanFileForm
from django import forms
from map_gallery.models import Map
from taggit.forms import TagField


class ResourceFormMixin(forms.ModelForm):
    tags = TagField(required=False)
    is_map = True
    class Meta:
        model = Map
        fields = [
            "file",
            "name",
            "description",
            "tags"
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""


class UpdateForm(ResourceFormMixin):
    """GeoPackage Update Form."""
