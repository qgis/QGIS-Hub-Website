from base.models.processing_models import Resource, ResourceReview
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

MAPS_STORAGE_PATH = getattr(settings, "HUB_STORAGE_PATH", "maps/%Y")
ALLOWED_IMAGE_EXTENSIONS = [
  "png",
  "jpg",
  "jpeg",
  "gif",
  "svg",
  "webp",
  "tiff",
  "bmp",
]

class Map(Resource):
  """
  Model for storing map submissions
  """

  name = models.CharField(
    _("Name"),
    help_text=_(
      "A short name for the map."
    ),
    max_length=256,
    unique=True,
  )
  description = models.TextField(
    _("Description"),
    help_text=_("A short narrative of how QGIS was used to create the map."),
    max_length=5000
  )
  file = models.ImageField(
    _("Map Image File"),
    help_text=_("An image file of the map. The file size must be less than 10MB."),
    upload_to=MAPS_STORAGE_PATH,
    validators=[FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)],
    null=False,
    blank=False,
  )

  def get_absolute_url(self):
    return reverse("map_detail", args=(self.id,))

class Review(ResourceReview):
  # map
  resource = models.ForeignKey(
      Map,
      verbose_name=_("Map"),
      help_text=_("The reviewed Map."),
      blank=True,
      null=True,
      on_delete=models.CASCADE,
  )