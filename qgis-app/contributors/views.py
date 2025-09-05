from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import get_all_commit_counts, get_commit_count_by_author
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CommitCountList(APIView):
  """
  Handles GET requests to retrieve commit counts for all authors in a given repository.

  Parameters:
  - repo: The name of the repository.

  Optional Query Parameters:
  - since: (string) The start date for filtering commits (e.g., '2023-01-01').
  - until: (string) The end date for filtering commits (e.g., '2023-12-31').

  Returns:
  - A JSON response containing commit counts per author within the specified date range.
  """
  @swagger_auto_schema(
    operation_description="Retrieve commit counts for all authors in a given repository.",
    manual_parameters=[
      openapi.Parameter(
        'since', openapi.IN_QUERY, description="Start date for filtering commits (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=False
      ),
      openapi.Parameter(
        'until', openapi.IN_QUERY, description="End date for filtering commits (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=False
      ),
    ],
    responses={200: openapi.Response(
      description="Commit counts per author",
      examples={
        "application/json": [
          {"author": "John Doe", "commit_count": 42},
          {"author": "Jane Smith", "commit_count": 35}
        ]
      }
    )}
  )
  def get(self, request, repo):
    since = request.query_params.get("since")
    until = request.query_params.get("until")

    commit_counts = get_all_commit_counts(repo, since, until)
    return Response(commit_counts)

class CommitCountByAuthor(APIView):
  """
  Handles GET requests to retrieve the commit count for a specific author in a given repository.

  Parameters:
  - repo: The name of the repository.
  - author: Comma-separated list of author names. 
    The local git command doesn't handle the GitHub username, 
    but only the Author (which is the name/email used in the git commit).
    However, the same contributor might have changed their Author
    information over time (this is usually set with git config user.name).

  Optional Query Parameters:
  - since: (string) The start date for filtering commits (e.g., '2023-01-01').
  - until: (string) The end date for filtering commits (e.g., '2023-12-31').

  Returns:
  - A JSON response containing the commit count for the specified author within the given date range.
  """

  @swagger_auto_schema(
    operation_description="Retrieve the commit count for a specific author in a given repository.",
    manual_parameters=[
      openapi.Parameter(
        'since', openapi.IN_QUERY, description="Start date for filtering commits (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=False
      ),
      openapi.Parameter(
        'until', openapi.IN_QUERY, description="End date for filtering commits (YYYY-MM-DD)", type=openapi.TYPE_STRING, required=False
      ),
    ],
    responses={200: openapi.Response(
      description="Commit count for the specified author",
      examples={
        "application/json": {"author": "John Doe", "commit_count": 42}
      }
    )}
  )
  def get(self, request, repo, author):
    since = request.query_params.get("since")
    until = request.query_params.get("until")

    commit_count = get_commit_count_by_author(repo, author, since, until)
    return Response(commit_count)
