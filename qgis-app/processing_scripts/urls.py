from django.urls import path
from processing_scripts.views import (
    ProcessingScriptCreateView,
    ProcessingScriptDeleteView,
    ProcessingScriptDetailView,
    ProcessingScriptDownloadView,
    ProcessingScriptListView,
    ProcessingScriptRequireActionListView,
    ProcessingScriptReviewView,
    ProcessingScriptUnapprovedListView,
    ProcessingScriptUpdateView,
    ProcessingScriptByTagView,
    ProcessingScriptUnapproveView,
    processing_script_nav_content,
)

urlpatterns = [
    #  ProcessingScript
    path("", ProcessingScriptListView.as_view(), name="processing_script_list"),
    path("add/", ProcessingScriptCreateView.as_view(), name="processing_script_create"),
    path("<int:pk>/", ProcessingScriptDetailView.as_view(), name="processing_script_detail"),
    path("<int:pk>/update/", ProcessingScriptUpdateView.as_view(), name="processing_script_update"),
    path("<int:pk>/delete/", ProcessingScriptDeleteView.as_view(), name="processing_script_delete"),
    path("<int:pk>/review/", ProcessingScriptReviewView.as_view(), name="processing_script_review"),
    path("<int:pk>/unapprove/", ProcessingScriptUnapproveView.as_view(), name="processing_script_unapprove"),
    path("<int:pk>/download/", ProcessingScriptDownloadView.as_view(), name="processing_script_download"),
    path("unapproved/", ProcessingScriptUnapprovedListView.as_view(), name="processing_script_unapproved"),
    path(
        "require_action/",
        ProcessingScriptRequireActionListView.as_view(),
        name="processing_script_require_action",
    ),
    path("tags/<processing_script_tag>/", ProcessingScriptByTagView.as_view(), name="processingscript_tag"),
    # JSON
    path("sidebarnav/", processing_script_nav_content, name="processing_script_nav_content"),
]
