"""
GitHub API - Issue Operations Module

Handles all issue-related GitHub API operations.
"""

import logging
import requests
from . import core

logger = logging.getLogger(__name__)


def count_issues_created(owner, repo, username):
    """
    Count total issues created by a specific user in a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the issue creator.

    Returns:
        int: Number of issues created. Returns 0 on error.
    """
    q = f"repo:{owner}/{repo} type:issue author:{username}"
    url = f"{core.GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}

    try:
        resp = requests.get(url, headers=core.HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("total_count", 0)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error counting issues created by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0
    except ValueError as e:
        logger.error(f"Failed to decode JSON for issues by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0


def count_issues_resolved_by(owner, repo, username):
    """
    Count issues resolved (closed) by a specific user in a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the user who closed the issues.

    Returns:
        int: Number of issues resolved. Returns 0 on error.
    """
    url = f"{core.GITHUB_API}/repos/{owner}/{repo}/issues"
    params = {"state": "closed", "per_page": 100}
    issues = core.paginated_get(url, params=params)

    if isinstance(issues, dict):
        core._handle_api_error_response(issues, f"Error fetching resolved issues for {username} in {owner}/{repo}")
        return 0

    count = 0
    for issue in issues:
        if "pull_request" in issue:
            continue
        closed_by = issue.get("closed_by")
        if closed_by and closed_by.get("login", "").lower() == username.lower():
            count += 1
    return count
