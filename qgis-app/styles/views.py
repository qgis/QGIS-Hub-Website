import json

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
    resource_nav_content,
    resource_notify,
)
from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from styles.file_handler import read_xml_style, get_gpl_name
from styles.forms import UpdateForm, UploadForm
from styles.models import Review, Style, StyleType
from urllib.parse import unquote


class ResourceMixin:
    """Mixin class for Style."""

    model = Style

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = "Style"

    # The url name in urls.py should start start with this value
    resource_name_url_base = "style"

    # The index of the submenu in the settings variable HUB_SUBMENU
    hub_submenu_index = 0


class StyleCreateView(ResourceMixin, ResourceBaseCreateView):
    """
    Create a new style
    """

    form_class = UploadForm

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        if obj.file.name.lower().endswith(".gpl"):
            style_name = get_gpl_name(obj.file)
            style_type_str = "Color Palette"
        else:
            xml_parse = read_xml_style(obj.file)
            if xml_parse:
                style_name = xml_parse["name"]
                style_type_str = xml_parse["type"]
        if style_name and style_type_str:
            # check if name exists
            name_exist = Style.objects.filter(name__iexact=style_name).exists()
            if name_exist:
                obj.name = "%s_%s" % (
                    style_name.title(),
                    get_random_string(length=5),
                )
            else:
                obj.name = style_name.title()
            style_type = StyleType.objects.filter(symbol_type=style_type_str).first()
            if not style_type:
                style_type = StyleType.objects.create(
                    symbol_type=style_type_str,
                    name=style_type_str.title(),
                    description="Automatically created from '"
                    "'an uploaded Style file",
                )
            obj.style_type = style_type
        obj.save()
        # Without this next line the tags won't be saved.
        form.save_m2m()
        resource_notify(obj, self.resource_name)
        msg = _("The Style has been successfully created.")
        messages.success(self.request, msg, "success", fail_silently=True)
        return HttpResponseRedirect(reverse("style_detail", kwargs={"pk": obj.id}))


class StyleDetailView(ResourceMixin, ResourceBaseDetailView):
    """Style Detail View"""


class StyleUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """
    Update a style
    """

    form_class = UpdateForm

    def form_valid(self, form):
        """
        Update the style type according to the style XML file.
        """

        obj = form.save(commit=False)
        if obj.file.name.lower().endswith(".gpl"):
            style_type_str = "Color Palette"
        else:
            xml_parse = read_xml_style(obj.file)
            style_type_str = xml_parse["type"]
        if style_type_str:
            obj.style_type = StyleType.objects.filter(
                symbol_type=style_type_str
            ).first()
        obj.require_action = False
        obj.save()
        # Without this next line the tags won't be saved.
        form.save_m2m()
        resource_notify(obj, created=False, resource_type=self.resource_name)
        msg = _("The Style has been successfully updated.")
        messages.success(self.request, msg, "success", fail_silently=True)
        return HttpResponseRedirect(reverse_lazy("style_detail", kwargs={"pk": obj.id}))


class StyleUnapproveView(ResourceMixin, ResourceBaseUnapproveView):
    """
    Unapprove a style
    """


class StyleListView(ResourceMixin, ResourceBaseListView):
    """Style ListView."""


class StyleByTagView(StyleListView):
    """Display StyleListView filtered on style tag"""

    def get_filtered_queryset(self, qs):
        response = qs.filter(tagged_items__tag__slug=unquote(self.kwargs["style_tag"]))
        return response

    def get_queryset(self):
        qs = super().get_queryset()
        return self.get_filtered_queryset(qs)

    def get_context_data(self, **kwargs):
        context = super(StyleByTagView, self).get_context_data(**kwargs)
        context.update(
            {
                "title": _("Style tagged with: %s") % unquote(self.kwargs["style_tag"]),
                "page_title": _("Tag: %s") % unquote(self.kwargs["style_tag"])
            }
        )
        return context

class StyleByTypeListView(StyleListView):
    """Display StyleListView filtered on style type"""

    def get_queryset(self):
        qs = super().get_queryset()
        style_type = self.kwargs["style_type"]
        return qs.filter(style_type__name=style_type)

    def get_context_data(self, **kwargs):
        """
        Override get_context_data.

        Add 'title' to be displayed as page title
        """

        context = super(StyleByTypeListView, self).get_context_data(**kwargs)
        context["title"] = "%s Styles" % (self.kwargs["style_type"],)
        return context


class StyleUnapprovedListView(ResourceMixin, ResourceBaseUnapprovedListView):
    """Unapproved Style ListView."""


class StyleRequireActionListView(ResourceMixin, ResourceBaseRequireActionListView):
    """Style requires action."""


class StyleDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """Delete a style."""


class StyleReviewView(ResourceMixin, ResourceBaseReviewView):
    """Create a review"""


class StyleDownloadView(ResourceMixin, ResourceBaseDownload):
    """Download a style"""


def style_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response


@never_cache
def style_type_list(request):
    media_path = getattr(settings, "MEDIA_URL")
    qs = StyleType.objects.all()
    qs_json = serializers.serialize("json", qs)
    qs_load = json.loads(qs_json)
    qs_add = {"qs": qs_load, "icon_url": media_path}
    qs_json = json.dumps(qs_add)
    return HttpResponse(qs_json, content_type="application/json")
