from django.urls import path
from geopackages.views import (
    GeopackageCreateView,
    GeopackageDeleteView,
    GeopackageDetailView,
    GeopackageDownloadView,
    GeopackageListView,
    GeopackageRequireActionListView,
    GeopackageReviewView,
    GeopackageUnapprovedListView,
    GeopackageUpdateView,
    GeopackageByTagView,
    GeopackageUnapproveView,
    geopackage_nav_content,
)

urlpatterns = [
    #  GeoPackage
    path("", GeopackageListView.as_view(), name="geopackage_list"),
    path("add/", GeopackageCreateView.as_view(), name="geopackage_create"),
    path("<int:pk>/", GeopackageDetailView.as_view(), name="geopackage_detail"),
    path("<int:pk>/update/", GeopackageUpdateView.as_view(), name="geopackage_update"),
    path("<int:pk>/delete/", GeopackageDeleteView.as_view(), name="geopackage_delete"),
    path("<int:pk>/review/", GeopackageReviewView.as_view(), name="geopackage_review"),
    path("<int:pk>/unapprove/", GeopackageUnapproveView.as_view(), name="geopackage_unapprove"),
    path(
        "<int:pk>/download/",
        GeopackageDownloadView.as_view(),
        name="geopackage_download",
    ),
    path(
        "unapproved/",
        GeopackageUnapprovedListView.as_view(),
        name="geopackage_unapproved",
    ),
    path(
        "require_action/",
        GeopackageRequireActionListView.as_view(),
        name="geopackage_require_action",
    ),
    path("tags/<geopackage_tag>/", GeopackageByTagView.as_view(), name="geopackage_tag"),
    # JSON
    path("sidebarnav/", geopackage_nav_content, name="geopackage_nav_content"),
]
