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
  ResourceBaseUnapproveView,
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

from screenshots.models import Review, Screenshot
from screenshots.forms import UpdateForm, UploadForm
from map_gallery.validator import is_valid_image, is_valid_svg

from base.permissions import MapPublisherRequiredMixin


class ResourceMixin:
  """Mixin class for Screenshot."""

  model = Screenshot
  review_model = Review
  resource_name = "Screenshot"
  resource_name_url_base = "screenshot"
  hub_submenu_index = 6


class ScreenshotCreateView(ResourceMixin, ResourceBaseCreateView):
  """Upload a Screenshot File"""

  form_class = UploadForm

  def form_valid(self, form):
    obj = form.save(commit=False)
    obj.creator = self.request.user
  
    # Check if the uploaded file is a valid image or SVG
    print(obj.file.name.lower(), "##########")
    if obj.file.name.lower().endswith(".svg"):
      is_valid_svg(obj.file)
    else:
      is_valid_image(obj.file)
    obj.save()
    form.save_m2m()
    resource_notify(obj, self.resource_name)
    msg = _("The Screenshot has been successfully created.")
    messages.success(self.request, msg, "success", fail_silently=True)
    return HttpResponseRedirect(reverse("screenshot_detail", kwargs={"pk": obj.id}))


class ScreenshotDetailView(ResourceMixin, ResourceBaseDetailView):
  """Screenshot Detail View"""


class ScreenshotUpdateView(ResourceMixin, ResourceBaseUpdateView):
  """Update the Screenshot"""

  form_class = UpdateForm

  def form_valid(self, form):
    obj = form.save(commit=False)
    obj.require_action = False
    obj.approved = False

    # Check if the uploaded file is a valid image or SVG
    print(obj.file.name.lower())
    if obj.file.name.lower().endswith(".svg"):
      is_valid_svg(obj.file)
    else:
      is_valid_image(obj.file)
    obj.save()
    form.save_m2m()
    resource_notify(obj, created=False, resource_type=self.resource_name)
    msg = _("The Screenshot has been successfully updated.")
    messages.success(self.request, msg, "success", fail_silently=True)
    return HttpResponseRedirect(reverse("screenshot_detail", kwargs={"pk": obj.id}))


class ScreenshotUnapproveView(ResourceMixin, ResourceBaseUnapproveView):
  """Unapprove a Screenshot"""


class ScreenshotListView(ResourceMixin, ResourceBaseListView):
  """Approved Screenshot ListView"""


class ScreenshotUnapprovedListView(ResourceMixin, ResourceBaseUnapprovedListView):
  """Unapproved Screenshot ListView"""


class ScreenshotRequireActionListView(ResourceMixin, ResourceBaseRequireActionListView):
  """Screenshot Requires Action"""


class ScreenshotDeleteView(ResourceMixin, ResourceBaseDeleteView):
  """Delete a Screenshot."""


class ScreenshotReviewView(ResourceMixin, ResourceBaseReviewView):
  """Create a review"""


class ScreenshotDownloadView(ResourceMixin, ResourceBaseDownload):
  """Download a Screenshot"""


class ScreenshotByTagView(ScreenshotListView):
  """Display ScreenshotListView filtered on screenshot tag"""

  def get_filtered_queryset(self, qs):
    response = qs.filter(tagged_items__tag__slug=unquote(self.kwargs["screenshot_tag"]))
    return response

  def get_queryset(self):
    qs = super().get_queryset()
    return self.get_filtered_queryset(qs)

  def get_context_data(self, **kwargs):
    context = super(ScreenshotByTagView, self).get_context_data(**kwargs)
    context.update(
      {
        "title": _("Screenshot tagged with: %s") % unquote(self.kwargs["screenshot_tag"]),
        "page_title": _("Tag: %s") % unquote(self.kwargs["screenshot_tag"])
      }
    )
    return context


class ScreenshotTogglePublishView(MapPublisherRequiredMixin, ResourceMixin, ResourceBaseContextMixin, View):
  """Publish/Unpublish a Screenshot"""

  def get_object(self):
    return self.model.objects.get(pk=self.kwargs["pk"])

  def get(self, request, *args, **kwargs):
    obj = self.get_object()
    context = self.get_context_data()
    context["object"] = obj
    return render(request, "base/confirm_publish.html", context)

  def post(self, request, *args, **kwargs):
    obj = self.get_object()
    obj.is_publishable = not obj.is_publishable
    obj.save()
    msg = _("The Screenshot's publishable status has been successfully updated.")
    messages.success(self.request, msg, "success", fail_silently=True)
    return HttpResponseRedirect(reverse("screenshot_detail", kwargs={"pk": obj.id}))


def screenshot_nav_content(request):
  model = ResourceMixin.model
  response = resource_nav_content(request, model)
  return response
