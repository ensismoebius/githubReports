"""
GitHub API - Commit Operations Module

Handles all commit-related GitHub API operations.
"""

import logging
from . import core

logger = logging.getLogger(__name__)


def count_commits(owner, repo, username):
    """
    Count total commits made by a specific user in a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the author.

    Returns:
        int: Number of commits. Returns 0 on error.
    """
    url = f"{core.GITHUB_API}/repos/{owner}/{repo}/commits"
    params = {"author": username, "per_page": 100}
    commits = core.paginated_get(url, params=params)

    if isinstance(commits, dict):
        core._handle_api_error_response(commits, f"Error fetching commits for {username} in {owner}/{repo}")
        return 0

    return len(commits)


def list_commits(owner, repo, username):
    """
    List all commits made by a specific user in a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the author.

    Returns:
        list: List of commit objects. Returns empty list on error.
    """
    url = f"{core.GITHUB_API}/repos/{owner}/{repo}/commits"
    params = {"author": username, "per_page": 100}
    commits = core.paginated_get(url, params=params)

    if isinstance(commits, dict):
        core._handle_api_error_response(commits, f"Error fetching commits for {username} in {owner}/{repo}")
        return []

    return commits
