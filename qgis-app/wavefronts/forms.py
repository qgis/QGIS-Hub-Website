from base.forms.processing_forms import ResourceBaseCleanFileForm
from django import forms
from wavefronts.models import Wavefront
from wavefronts.validator import WavefrontValidator
from taggit.forms import TagField


class ResourceFormMixin(forms.ModelForm):
    tags = TagField(required=False)
    is_3d = True
    class Meta:
        model = Wavefront
        fields = [
            "file",
            "thumbnail_image",
            "name",
            "description",
            "tags"
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""

    file_path = ""

    def clean_file(self):
        model_file = super(UploadForm, self).clean_file()
        if model_file:
            self.file_path = WavefrontValidator(model_file).validate()
        return model_file


class UpdateForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Model Update Form."""

    file_path = ""

    def clean_file(self):
        model_file = super(UpdateForm, self).clean_file()
        if model_file:
            self.file_path = WavefrontValidator(model_file).validate()
        return model_file
