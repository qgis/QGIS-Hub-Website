from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import get_all_commit_counts, get_commit_count_by_author

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
    def get(self, request, repo, author):
        since = request.query_params.get("since")
        until = request.query_params.get("until")

        commit_count = get_commit_count_by_author(repo, author, since, until)
        return Response(commit_count)
