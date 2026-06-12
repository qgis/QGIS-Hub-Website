import os

from base.models.processing_models import Resource, ResourceReview
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

SCRIPTS_STORAGE_PATH = getattr(settings, "HUB_STORAGE_PATH", "processing_scripts/%Y")


class PyQtVersion(models.Model):
    """PyQt Version model for tracking compatibility"""

    name = models.CharField(
        _("Name"),
        help_text=_("PyQt version name (e.g., PyQt5, PyQt6)"),
        max_length=50,
        unique=True,
    )

    description = models.TextField(
        _("Description"),
        help_text=_("A short description of this PyQt version."),
        max_length=500,
        blank=True,
        null=True,
    )

    # Ordering
    order = models.IntegerField(
        _("Order"),
        help_text=_("Order value for display sorting."),
        default=0,
    )

    class Meta:
        ordering = ("order", "name")
        verbose_name = _("PyQt Version")
        verbose_name_plural = _("PyQt Versions")

    def __str__(self):
        return self.name


class ProcessingScript(Resource):
    """
    Model for storing processing scripts
    """

    # thumbnail
    thumbnail_image = models.ImageField(
        _("Thumbnail"),
        help_text=_(
            "Please upload an image that demonstrate this Script. Max size is 2MB."
        ),
        blank=False,
        null=False,
        upload_to=SCRIPTS_STORAGE_PATH,
    )

    # file
    file = models.FileField(
        _("Processing script file"),
        help_text=_("A Python file. The filesize must be less than 1MB."),
        upload_to=SCRIPTS_STORAGE_PATH,
        validators=[FileExtensionValidator(allowed_extensions=["py"])],
        null=False,
    )

    # plugin dependencies
    dependencies = models.TextField(
        _("Plugin dependencies"),
        help_text=_("Comma-separated list for the plugin the script needs"),
        blank=True,
        null=True,
    )

    # PyQt version compatibility - multiple versions supported
    pyqt_versions = models.ManyToManyField(
        PyQtVersion,
        related_name="processing_scripts",
        verbose_name=_("PyQt Versions"),
        help_text=_("The PyQt versions this script is compatible with"),
        blank=True,
    )

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def get_absolute_url(self):
        return reverse("processing_script_detail", args=(self.id,))

    def get_file_content(self):
        with open(self.file.path, "r") as file:
            return file.read()


class Review(ResourceReview):
    """
    A Model Review for ProcessingScript.
    """

    # Model resource
    resource = models.ForeignKey(
        ProcessingScript,
        verbose_name=_("Processing Script"),
        help_text=_("The reviewed Processing Script"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
