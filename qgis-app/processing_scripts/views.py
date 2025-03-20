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
from processing_scripts.forms import UpdateForm, UploadForm
from processing_scripts.models import ProcessingScript, Review
from django.utils.translation import gettext_lazy as _
from urllib.parse import unquote
from django.conf import settings


class ResourceMixin:
    """Mixin class for Processing Script."""

    model = ProcessingScript

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = "Processing Script"

    # The url name in urls.py should start with this value
    resource_name_url_base = "processing_script"

    # The index of the submenu in the settings variable HUB_SUBMENU
    hub_submenu_index = 6


class ProcessingScriptCreateView(ResourceMixin, ResourceBaseCreateView):
    """Upload a ProcessingScript File"""

    form_class = UploadForm


class ProcessingScriptDetailView(ResourceMixin, ResourceBaseDetailView):
    """ProcessingScript Detail View"""


class ProcessingScriptUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """Update the ProcessingScript"""

    form_class = UpdateForm


class ProcessingScriptListView(ResourceMixin, ResourceBaseListView):
    """Approved ProcessingScript ListView"""


class ProcessingScriptUnapprovedListView(ResourceMixin, ResourceBaseUnapprovedListView):
    """Unapproved ProcessingScript ListView"""


class ProcessingScriptRequireActionListView(ResourceMixin, ResourceBaseRequireActionListView):
    """ProcessingScript Requires Action"""


class ProcessingScriptDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """Delete a ProcessingScript."""


class ProcessingScriptReviewView(ResourceMixin, ResourceBaseReviewView):
    """Create a review"""


class ProcessingScriptDownloadView(ResourceMixin, ResourceBaseDownload):
    """Download a ProcessingScript"""


class ProcessingScriptByTagView(ProcessingScriptListView):
    """Display ProcessingScriptListView filtered on processing_script_tag"""

    def get_filtered_queryset(self, qs):
        response = qs.filter(tagged_items__tag__slug=unquote(self.kwargs["processing_script_tag"]))
        return response

    def get_queryset(self):
        qs = super().get_queryset()
        return self.get_filtered_queryset(qs)

    def get_context_data(self, **kwargs):
        context = super(ProcessingScriptByTagView, self).get_context_data(**kwargs)
        context.update(
            {
                "title": _("ProcessingScript tagged with: %s") % unquote(self.kwargs["processing_script_tag"]),
                "page_title": _("Tag: %s") % unquote(self.kwargs["processing_script_tag"])
            }
        )
        return context

def processing_script_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response
