from django.urls import path
from screenshots.views import (
  ScreenshotCreateView,
  ScreenshotDeleteView,
  ScreenshotDetailView,
  ScreenshotDownloadView,
  ScreenshotListView,
  ScreenshotRequireActionListView,
  ScreenshotReviewView,
  ScreenshotUnapprovedListView,
  ScreenshotUpdateView,
  ScreenshotUnapproveView,
  ScreenshotByTagView,
  ScreenshotTogglePublishView,
  screenshot_nav_content,
)

urlpatterns = [
  # Screenshot
  path("", ScreenshotListView.as_view(), name="screenshot_list"),
  path("add/", ScreenshotCreateView.as_view(), name="screenshot_create"),
  path("<int:pk>/", ScreenshotDetailView.as_view(), name="screenshot_detail"),
  path("<int:pk>/update/", ScreenshotUpdateView.as_view(), name="screenshot_update"),
  path("<int:pk>/unapprove/", ScreenshotUnapproveView.as_view(), name="screenshot_unapprove"),
  path("<int:pk>/delete/", ScreenshotDeleteView.as_view(), name="screenshot_delete"),
  path("<int:pk>/review/", ScreenshotReviewView.as_view(), name="screenshot_review"),
  path(
    "<int:pk>/download/",
    ScreenshotDownloadView.as_view(),
    name="screenshot_download",
  ),
  path(
    "<int:pk>/toggle-publish/",
    ScreenshotTogglePublishView.as_view(),
    name="screenshot_toggle_publish",
  ),
  path(
    "unapproved/",
    ScreenshotUnapprovedListView.as_view(),
    name="screenshot_unapproved",
  ),
  path(
    "require_action/",
    ScreenshotRequireActionListView.as_view(),
    name="screenshot_require_action",
  ),
  path("tags/<screenshot_tag>/", ScreenshotByTagView.as_view(), name="screenshot_tag"),
  # JSON
  path("sidebarnav/", screenshot_nav_content, name="screenshot_nav_content"),
]
