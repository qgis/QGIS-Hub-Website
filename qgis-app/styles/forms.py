from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from styles.file_handler import validator, gpl_validator
from styles.models import Style
from taggit.forms import TagField
from base.forms.processing_forms import ResourceBaseCleanFileForm


class ResourceFormMixin(forms.ModelForm):
    tags = TagField(required=False)
    class Meta:
        model = Style
        fields = [
            "file",
            "thumbnail_image",
            "description",
            "tags"
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """
    Style Upload Form.
    """
    def clean_file(self):
        """
        Cleaning file field data.
        """

        style_file = super(UploadForm, self).clean_file()
        if style_file.name.lower().endswith('.gpl'):
            gpl_validator(style_file)
        else:
            style = validator(style_file.file)
            if not style:
                raise ValidationError(
                    _("Undefined style type. " "Please register your style type.")
                )
        return style_file


class UpdateForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Style Update Form."""
    class Meta(ResourceFormMixin.Meta):
        fields = ResourceFormMixin.Meta.fields[:2] + ["name"] + ResourceFormMixin.Meta.fields[2:]

    def clean_file(self):
        """
        Cleaning file field data only if the file has been updated.
        """
        if 'file' in self.changed_data:
            style_file = super(UpdateForm, self).clean_file()
            if style_file.name.lower().endswith('.gpl'):
                gpl_validator(style_file)
            else:
                style = validator(style_file.file)
                if not style:
                    raise ValidationError(
                        _("Undefined style type. " "Please register your style type.")
                    )
            return style_file
        return self.cleaned_data.get('file')

class StyleReviewForm(forms.Form):
    """
    Style Review Form.
    """

    CHOICES = [("approve", "Approve"), ("reject", "Reject")]
    approval = forms.ChoiceField(
        required=True, choices=CHOICES, widget=forms.RadioSelect, initial="approve"
    )
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Please provide clear feedback "
                "if you decided to not approve this style.",
                "rows": "5",
            }
        )
    )


class StyleSearchForm(forms.Form):
    """
    Search Form
    """

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "search-query", "placeholder": "Search"}
        ),
    )
