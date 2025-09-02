import os
import subprocess
from pathlib import Path
from django.conf import settings

REPO_BASE = Path(settings.SITE_ROOT) / 'qgis_repos'  # where you mirror repos

def fetch_repo(repo_name: str):
    repo_path = REPO_BASE / repo_name
    subprocess.run(["git", "-C", str(repo_path), "fetch", "--all"], check=True)

# Get all commit counts for repo
def get_all_commit_counts(repo_name: str, since=None, until=None):
    """
    Retrieves the commit counts for all authors in a given Git repository within an optional date range.
    Parameters:
      repo_name (str): The name of the repository to analyze.
      since (str, optional): The start date (inclusive) for filtering commits (e.g., '2023-01-01'). Defaults to None.
      until (str, optional): The end date (inclusive) for filtering commits (e.g., '2023-12-31'). Defaults to None.
    Returns:
      list: A list of commit counts for each author found in the repository within the specified date range.
    """

    repo_path = REPO_BASE / repo_name
    fetch_repo(repo_name)
    # Get all authors
    cmd_authors = ["git", "-C", str(repo_path), "log", "--pretty=format:%an"]
    if since:
        cmd_authors.append(f"--since={since}")
    if until:
        cmd_authors.append(f"--until={until}")
    result = subprocess.run(cmd_authors, capture_output=True, text=True, check=True)
    authors = set(result.stdout.splitlines())
    # Remove empty author names
    authors = {a for a in authors if a}
    # Get commit count for each author
    counts = []
    for author in authors:
        counts.append(get_commit_count_by_author(repo_name, author, since, until, fetch_all=False))
    return counts

# Get commit count by author using git rev-list
def get_commit_count_by_author(repo_name: str, author: str, since=None, until=None, fetch_all=True):
  """
  Retrieves the number of commits made by a specific author (or authors) in a given Git repository,
  optionally within a specified date range, and returns the date of the most recent commit.
  Args:
    repo_name (str): The name of the repository to analyze.
    author (str): The author name or a comma-separated list of author names to filter commits by.
    since (str, optional): The start date (inclusive) for filtering commits (e.g., '2023-01-01').
    until (str, optional): The end date (inclusive) for filtering commits (e.g., '2023-12-31').
    fetch_all (bool, optional): If True, fetches the latest changes from the remote repository before counting commits.
  Returns:
    dict: A dictionary containing:
      - "repo" (str): The repository name.
      - "author" (str): The author(s) used for filtering.
      - "commits" (int): The number of commits found for the author(s).
      - "last_commit_date" (str or None): The date of the most recent commit by the author(s) in ISO format, or None if no commits found.
  """
  repo_path = REPO_BASE / repo_name
  if fetch_all:
    fetch_repo(repo_name)
  if "," in author:
    authors = author.split(",")
    author_regex = "\|".join([a.strip() for a in authors if a.strip()])
    author_arg = f"--author={author_regex}"
  else:
    author_arg = f"--author={author}"
  cmd = [
    "git", "-C", str(repo_path),
    "rev-list",
    author_arg,
    "--no-merges",
    "HEAD"
  ]
  if since:
    cmd.append(f"--since={since}")
  if until:
    cmd.append(f"--until={until}")
  result = subprocess.run(cmd, capture_output=True, text=True, check=True)
  lines = result.stdout.splitlines()
  commits = len(lines)
  last_commit_date = None
  if lines:
    # Get the date of the most recent commit
    sha = lines[0]
    date_cmd = [
      "git", "-C", str(repo_path),
      "show", "-s", "--format=%ad", "--date=iso", sha
    ]
    date_result = subprocess.run(date_cmd, capture_output=True, text=True, check=True)
    last_commit_date = date_result.stdout.strip()
  return {
    "repo": repo_name,
    "author": author,
    "commits": commits,
    "last_commit_date": last_commit_date
  }
