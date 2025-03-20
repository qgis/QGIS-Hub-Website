from base.models.processing_models import Resource, ResourceReview
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
import os

SCRIPTS_STORAGE_PATH = getattr(settings, "HUB_STORAGE_PATH", "processing_scripts/%Y")

class ProcessingScript(Resource):
  """
  Model for storing processing scripts
  """
  # thumbnail
  thumbnail_image = models.ImageField(
      _("Thumbnail"),
      help_text=_("Please upload an image that demonstrate this Script"),
      blank=False,
      null=False,
      upload_to=SCRIPTS_STORAGE_PATH,
  )

  # file
  file = models.FileField(
      _("Processing script file"),
      help_text=_("A Python file. The filesize must less than 1MB "),
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


  def extension(self):
    name, extension = os.path.splitext(self.file.name)
    return extension

  def get_absolute_url(self):
    return reverse("processing_script_detail", args=(self.id,))
  
  def get_file_content(self):
    with open(self.file.path, 'r') as file:
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
