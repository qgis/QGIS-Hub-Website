from django.urls import path
from .views import CommitCountList, CommitCountByAuthor

urlpatterns = [
    path("<str:repo>/commit-counts/", CommitCountList.as_view(), name="commit-counts"),
    path("<str:repo>/commit-counts/<str:author>/", CommitCountByAuthor.as_view(), name="commit-count-by-author"),
]