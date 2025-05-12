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
        zip_file = super(UploadForm, self).clean_file()
        if zip_file:
            self.file_path = WavefrontValidator(zip_file).validate_wavefront()
        return zip_file


class UpdateForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Model Update Form."""

    def clean_file(self):
        zip_file = super(UpdateForm, self).clean_file()
        if zip_file:
            self.file_path = WavefrontValidator(zip_file).validate_wavefront()
        return zip_file
