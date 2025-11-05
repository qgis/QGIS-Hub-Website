import re
import subprocess
from pathlib import Path

from django.conf import settings

REPO_BASE = Path(settings.SITE_ROOT) / "qgis_repos"  # where you mirror repos

REPOS = [
    "QGIS-Website",
    "QGIS-Plugins-Website",
    "QGIS-Hub-Website",
    "QGIS-Planet-Website",
    "QGIS-Certification-Website",
    "QGIS-Changelog-Website",
    "QGIS-Members-Website",
    "QGIS-UC-Website",
    "QGIS-Feed-Website",
    "QGIS-Documentation",
    "QGIS",
]


def fetch_all_repos():
    for repo in REPOS:
        fetch_repo(repo)


def fetch_repo(repo_name: str):
    repo_path = REPO_BASE / repo_name
    subprocess.run(["git", "-C", str(repo_path), "fetch", "--all"], check=True)


# Get commit count by author using git rev-list
def get_commit_count_by_author(repo_name: str, author: str, since=None, until=None):
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
    # Use committer to exclude bots
    if "," in author:
        authors = author.split(",")
        escaped_authors = [re.escape(a.strip()) for a in authors if a.strip()]
        author_regex = "\\|".join(escaped_authors)
        author_arg = f"--author={author_regex}"
        committer_arg = f"--committer=GitHub\\|{author_regex}"
    else:
        escaped_author = re.escape(author)
        author_arg = f"--author={escaped_author}"
        committer_arg = f"--committer=GitHub\\|{escaped_author}"

    cmd = [
        "git",
        "-C",
        str(repo_path),
        "rev-list",
        author_arg,
        committer_arg,
        "--no-merges",
        "HEAD",
    ]
    if since:
        cmd.append(f"--since={since}")
    if until:
        cmd.append(f"--until={until}")

    # Run with proper encoding for special characters
    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        check=True, 
        encoding='utf-8', 
        errors='replace'
    )
    lines = result.stdout.splitlines()
    commits = len(lines)
    last_commit_date = None
    if lines:
        # Get the date of the most recent commit
        sha = lines[0]
        date_cmd = [
            "git",
            "-C",
            str(repo_path),
            "show",
            "-s",
            "--format=%ad",
            "--date=iso",
            sha,
        ]
        date_result = subprocess.run(
            date_cmd, 
            capture_output=True, 
            text=True, 
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        last_commit_date = date_result.stdout.strip()

    return {
        "repo": repo_name,
        "author": author,
        "commits": commits,
        "last_commit_date": last_commit_date,
    }
