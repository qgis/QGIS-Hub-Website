from base.models.processing_models import Resource, ResourceReview
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from map_gallery.models import ALLOWED_IMAGE_EXTENSIONS

SCREENSHOTS_STORAGE_PATH = getattr(settings, "HUB_STORAGE_PATH", "screenshots/%Y")

class Screenshot(Resource):
  """
  Model for storing screenshot submissions
  """

  name = models.CharField(
    _("Name"),
    help_text=_(
      "A short name for the screenshot."
    ),
    max_length=256,
    unique=True,
  )
  description = models.TextField(
    _("Description"),
    help_text=_(
      "Provide a concise description explaining what the screenshot "
      "demonstrates in QGIS, including relevant context or features highlighted."
    ),
    max_length=5000,
  )
  file = models.FileField(
    verbose_name=_("Screenshot Image File"),
    help_text=_(
      "An image file of the screenshot (static or animated GIF). "
      "The file size must be less than 10MB."
    ),
    upload_to=SCREENSHOTS_STORAGE_PATH,
    validators=[
      FileExtensionValidator(
        allowed_extensions=ALLOWED_IMAGE_EXTENSIONS
      )
    ],
    null=False,
    blank=False,
  )
  is_publishable = models.BooleanField(
    _("Is Publishable"),
    help_text=_("Is this screenshot eligible to be published on QGIS.org?"),
    default=False,
  )

  def get_absolute_url(self):
    return reverse("screenshot_detail", args=(self.id,))

class Review(ResourceReview):
  # screenshot
  resource = models.ForeignKey(
      Screenshot,
      verbose_name=_("Screenshot"),
      help_text=_("The reviewed Screenshot."),
      blank=True,
      null=True,
      on_delete=models.CASCADE,
  )