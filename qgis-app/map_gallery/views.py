
from base.views.processing_view import (
    ResourceBaseCreateView,
    ResourceBaseDeleteView,
    ResourceBaseDetailView,
    ResourceBaseDownload,
    ResourceBaseListView,
    ResourceBaseRequireActionListView,
    ResourceBaseReviewView,
    ResourceBaseUnapprovedListView,
    ResourceBaseUpdateView,
    resource_nav_content,
)
from urllib.parse import unquote
from django.utils.translation import gettext_lazy as _

from map_gallery.models import Review, Map
from map_gallery.forms import UpdateForm, UploadForm


class ResourceMixin:
  """Mixin class for Map."""

  model = Map

  review_model = Review

  # The resource_name will be displayed as the app name on web page
  resource_name = "Map"

  # The url name in urls.py should start start with this value
  resource_name_url_base = "map"

  # The index of the submenu in the settings variable HUB_SUBMENU
  hub_submenu_index = 5


class MapCreateView(ResourceMixin, ResourceBaseCreateView):
  """Upload a Map File"""

  form_class = UploadForm


class MapDetailView(ResourceMixin, ResourceBaseDetailView):
  """Map Detail View"""


class MapUpdateView(ResourceMixin, ResourceBaseUpdateView):
  """Update the Map"""

  form_class = UpdateForm


class MapListView(ResourceMixin, ResourceBaseListView):
  """Approved Map ListView"""


class MapUnapprovedListView(ResourceMixin, ResourceBaseUnapprovedListView):
  """Unapproved Map ListView"""


class MapRequireActionListView(ResourceMixin, ResourceBaseRequireActionListView):
  """Map Requires Action"""


class MapDeleteView(ResourceMixin, ResourceBaseDeleteView):
  """Delete a Map."""


class MapReviewView(ResourceMixin, ResourceBaseReviewView):
  """Create a review"""


class MapDownloadView(ResourceMixin, ResourceBaseDownload):
  """Download a Map"""

class MapByTagView(MapListView):
  """Display MapListView filtered on map tag"""

  def get_filtered_queryset(self, qs):
    response = qs.filter(tagged_items__tag__slug=unquote(self.kwargs["map_tag"]))
    return response

  def get_queryset(self):
    qs = super().get_queryset()
    return self.get_filtered_queryset(qs)

  def get_context_data(self, **kwargs):
    context = super(MapByTagView, self).get_context_data(**kwargs)
    context.update(
        {
            "title": _("Map tagged with: %s") % unquote(self.kwargs["map_tag"]),
            "page_title": _("Tag: %s") % unquote(self.kwargs["map_tag"])
        }
    )
    return context

def map_nav_content(request):
  model = ResourceMixin.model
  response = resource_nav_content(request, model)
  return response