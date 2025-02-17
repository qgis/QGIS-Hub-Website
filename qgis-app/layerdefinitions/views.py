from base.views.processing_view import (
    HttpResponse,
    HttpResponseRedirect,
    ResourceBaseCreateView,
    ResourceBaseDeleteView,
    ResourceBaseDetailView,
    ResourceBaseDownload,
    ResourceBaseListView,
    ResourceBaseRequireActionListView,
    ResourceBaseReviewView,
    ResourceBaseUnapprovedListView,
    ResourceBaseUpdateView,
    TemplateResponse,
    _,
    check_resources_access,
    get_object_or_404,
    messages,
    resource_nav_content,
    resource_notify,
    reverse_lazy,
    slugify,
)
from layerdefinitions.file_handler import get_provider, get_url_datasource
from layerdefinitions.forms import UpdateForm, UploadForm
from layerdefinitions.license import zipped_with_license
from layerdefinitions.models import LayerDefinition, Review
from django.utils.translation import gettext_lazy as _
from urllib.parse import unquote
from django.conf import settings


class ResourceMixin:
    """Mixin class for LayerDefinition."""

    model = LayerDefinition

    review_model = Review

    # The resource_name will be displayed as the app name on web page
    resource_name = "Layer Definition File"

    # The url name in urls.py should start start with this value
    resource_name_url_base = "layerdefinition"

    # The index of the submenu in the settings variable HUB_SUBMENU
    hub_submenu_index = 4


class LayerDefinitionCreateView(ResourceMixin, ResourceBaseCreateView):
    """Upload a Layer Definition File (.qlr)."""

    form_class = UploadForm
    is_custom_license_agreement = True

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.creator = self.request.user
        obj.url_datasource = get_url_datasource(obj.file.file)
        obj.provider = get_provider(obj.file.file)
        obj.save()
        # Without this next line the tags won't be saved.
        form.save_m2m()
        resource_notify(obj, resource_type=self.resource_name)
        msg = _(self.success_message)
        messages.success(self.request, msg, "success", fail_silently=True)
        return super(ResourceBaseCreateView, self).form_valid(form)


class LayerDefinitionDetailView(ResourceMixin, ResourceBaseDetailView):
    """Detail View"""

    license_template = "base/includes/layerdefinition/license.html"
    css = ("css/detail_page.css",)

    def get_context_data(self, **kwargs):
        context = super(LayerDefinitionDetailView, self).get_context_data()
        context["is_qlr"] = True
        return context


class LayerDefinitionUpdateView(ResourceMixin, ResourceBaseUpdateView):
    """Update View"""

    form_class = UpdateForm
    is_custom_license_agreement = True

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.require_action = False
        obj.approved = False
        obj.url_datasource = get_url_datasource(obj.file.file)
        obj.provider = get_provider(obj.file.file)
        obj.save()
        # Without this next line the tags won't be saved.
        form.save_m2m()
        resource_notify(obj, created=False, resource_type=self.resource_name)
        msg = _("The %s has been successfully updated." % self.resource_name)
        messages.success(self.request, msg, "success", fail_silently=True)
        url_name = "%s_detail" % self.resource_name_url_base
        return HttpResponseRedirect(reverse_lazy(url_name, kwargs={"pk": obj.id}))


class LayerDefinitionListView(ResourceMixin, ResourceBaseListView):
    """Approved Layer Definition File (.qlr) ListView"""


class LayerDefinitionUnapprovedListView(ResourceMixin, ResourceBaseUnapprovedListView):
    """Unapproved Layer Definition File (.qlr) ListView"""


class LayerDefinitionRequireActionListView(
    ResourceMixin, ResourceBaseRequireActionListView
):
    """Layer Definition File (.qlr) Requires Action"""


class LayerDefinitionDeleteView(ResourceMixin, ResourceBaseDeleteView):
    """Delete a Layer Definition File (.qlr)."""


class LayerDefinitionReviewView(ResourceMixin, ResourceBaseReviewView):
    """Create a review."""

class LayerDefinitionByTagView(LayerDefinitionListView):
    """Display LayerDefinitionListView filtered on layerdefinition tag"""

    def get_filtered_queryset(self, qs):
        response = qs.filter(tagged_items__tag__slug=unquote(self.kwargs["layerdefinition_tag"]))
        return response

    def get_queryset(self):
        qs = super().get_queryset()
        return self.get_filtered_queryset(qs)

    def get_context_data(self, **kwargs):
        context = super(LayerDefinitionByTagView, self).get_context_data(**kwargs)
        context.update(
            {
                "title": _("LayerDefinition tagged with: %s") % unquote(self.kwargs["layerdefinition_tag"]),
                "page_title": _("Tag: %s") % unquote(self.kwargs["layerdefinition_tag"])
            }
        )
        return context

class LayerDefinitionDownloadView(ResourceMixin, ResourceBaseDownload):
    """Download a Layer Definition File (.qlr)."""

    def get(self, request, *args, **kwargs):
        object = get_object_or_404(self.model, pk=self.kwargs["pk"])
        if not object.approved:
            if not check_resources_access(self.request.user, object):
                context = super(ResourceBaseDownload, self).get_context_data()
                context["object_name"] = object.name
                context["context"] = (
                    "Download failed. This %s is " "not approved" % self.resource_name
                )
                return TemplateResponse(request, self.template_name, context)
        else:
            object.increase_download_counter()
            object.save(update_fields=['download_count'])

        # zip the resource and license.txt
        zipfile = zipped_with_license(
            file=object.file.file.name,
            zip_subdir=object.name,
            custom_license=object.license,
        )

        response = HttpResponse(
            zipfile.getvalue(), content_type="application/x-zip-compressed"
        )
        response["Content-Disposition"] = "attachment; filename=%s.zip" % (
            slugify(object.name, allow_unicode=True)
        )
        return response


def layerdefinition_nav_content(request):
    model = ResourceMixin.model
    response = resource_nav_content(request, model)
    return response
