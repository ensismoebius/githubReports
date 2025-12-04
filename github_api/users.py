"""
GitHub API - User and Repository Operations Module

Handles user and repository-related GitHub API operations.
"""

import logging
import requests
from . import core

logger = logging.getLogger(__name__)


def user_exists(username):
    """
    Check if a GitHub username exists.

    Args:
        username (str): GitHub username to check.

    Returns:
        bool: True if user exists, False otherwise.
    """
    url = f"{core.GITHUB_API}/users/{username}"
    try:
        resp = requests.get(url, headers=core.HEADERS)
        if resp.status_code == 200:
            return True
        if resp.status_code == 404:
            logger.info(f"User {username} does not exist (404 Not Found).")
            return False
        resp.raise_for_status()
        return False
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"Error checking existence of user {username}: {e}", exc_info=True)
        return False


def get_collaborators(owner, repo):
    """
    Get all collaborators for a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.

    Returns:
        list: List of GitHub usernames (login). Returns empty list on error.
    """
    url = f"{core.GITHUB_API}/repos/{owner}/{repo}/collaborators"
    collaborators_data = core.paginated_get(url)

    if isinstance(collaborators_data, dict):
        core._handle_api_error_response(collaborators_data, f"Error fetching collaborators for {owner}/{repo}")
        return []
    elif not isinstance(collaborators_data, list):
        logger.error(f"Unexpected data type returned for collaborators.")
        return []

    return [c["login"] for c in collaborators_data]
