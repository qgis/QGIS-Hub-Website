
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
    ResourceBaseContextMixin,
    resource_nav_content,
    resource_notify,
)
from urllib.parse import unquote
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.shortcuts import render

from map_gallery.models import Review, Map
from map_gallery.forms import UpdateForm, UploadForm
from map_gallery.validator import is_valid_image

from base.permissions import ResourceManagerRequiredMixin


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

  def form_valid(self, form):
    obj = form.save(commit=False)
    obj.creator = self.request.user

    # Check if the uploaded file is a valid image
    is_valid_image(obj.file)

    obj.save()
    form.save_m2m()
    resource_notify(obj, self.resource_name)
    msg = _("The Map has been successfully created.")
    messages.success(self.request, msg, "success", fail_silently=True)
    return HttpResponseRedirect(reverse("map_detail", kwargs={"pk": obj.id}))


class MapDetailView(ResourceMixin, ResourceBaseDetailView):
  """Map Detail View"""


class MapUpdateView(ResourceMixin, ResourceBaseUpdateView):
  """Update the Map"""

  form_class = UpdateForm

  def form_valid(self, form):
    obj = form.save(commit=False)
    obj.require_action = False
    obj.approved = False

    # Check if the uploaded file is a valid image
    is_valid_image(obj.file)

    obj.save()
    # Without this next line the tags won't be saved.
    form.save_m2m()
    resource_notify(obj, created=False, resource_type=self.resource_name)
    msg = _("The Map has been successfully updated.")
    messages.success(self.request, msg, "success", fail_silently=True)
    return HttpResponseRedirect(reverse("map_detail", kwargs={"pk": obj.id}))

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

class MapTooglePublishView(ResourceManagerRequiredMixin, ResourceMixin, ResourceBaseContextMixin, View):
  """Publish/Unpublish a Map on QGIS.org"""

  def get_object(self):
    """Retrieve the object based on the primary key from the URL."""
    return self.model.objects.get(pk=self.kwargs["pk"])

  def get(self, request, *args, **kwargs):
    obj = self.get_object()
    context = self.get_context_data()
    context["object"] = obj
    return render(request, "base/confirm_publish.html", context)

  def post(self, request, *args, **kwargs):
    obj = self.get_object()
    obj.is_publishable = not obj.is_publishable  # Toggle the is_publishable value
    obj.save()
    msg = _("The Map's publishable status has been successfully updated.")
    messages.success(self.request, msg, "success", fail_silently=True)
    return HttpResponseRedirect(reverse("map_detail", kwargs={"pk": obj.id}))


def map_nav_content(request):
  model = ResourceMixin.model
  response = resource_nav_content(request, model)
  return response