from django.urls import path

from .views import CommitCountByAuthor, FetchAllRepo

urlpatterns = [
    path(
        "<str:repo>/commit-counts/<str:author>/",
        CommitCountByAuthor.as_view(),
        name="commit-count-by-author",
    ),
    path("fetch-all-repos/", FetchAllRepo.as_view(), name="fetch-all-repos"),
]
