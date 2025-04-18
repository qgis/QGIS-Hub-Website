from django.urls import path
from map_gallery.views import (
    MapCreateView,
    MapDeleteView,
    MapDetailView,
    MapDownloadView,
    MapListView,
    MapRequireActionListView,
    MapReviewView,
    MapUnapprovedListView,
    MapUpdateView,
    MapUnapproveView,
    MapByTagView,
    MapTooglePublishView,
    map_nav_content,
)

urlpatterns = [
    #  Map
    path("", MapListView.as_view(), name="map_list"),
    path("add/", MapCreateView.as_view(), name="map_create"),
    path("<int:pk>/", MapDetailView.as_view(), name="map_detail"),
    path("<int:pk>/update/", MapUpdateView.as_view(), name="map_update"),
    path("<int:pk>/unapprove/", MapUnapproveView.as_view(), name="map_unapprove"),
    path("<int:pk>/delete/", MapDeleteView.as_view(), name="map_delete"),
    path("<int:pk>/review/", MapReviewView.as_view(), name="map_review"),
    path(
        "<int:pk>/download/",
        MapDownloadView.as_view(),
        name="map_download",
    ),
    path(
        "<int:pk>/toogle-publish/",
        MapTooglePublishView.as_view(),
        name="map_toggle_publish",
    ),

    path(
        "unapproved/",
        MapUnapprovedListView.as_view(),
        name="map_unapproved",
    ),
    path(
        "require_action/",
        MapRequireActionListView.as_view(),
        name="map_require_action",
    ),
    path("tags/<map_tag>/", MapByTagView.as_view(), name="map_tag"),
    # JSON
    path("sidebarnav/", map_nav_content, name="map_nav_content"),
]
