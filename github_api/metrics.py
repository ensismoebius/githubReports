"""
GitHub API - Code Metrics and Comments Module

Handles code metrics and comment counting operations.
"""

import logging
import requests
from . import core
from . import commits

logger = logging.getLogger(__name__)


def count_comments(owner, repo, username):
    """
    Count total comments made by a user on issues and PRs in a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the commenter.

    Returns:
        int: Total count of comments. Returns 0 on error.
    """
    total_comments = 0

    # Count issue comments
    try:
        q_issues = f"repo:{owner}/{repo} type:issue commenter:{username}"
        url = f"{core.GITHUB_API}/search/issues"
        params_issues = {"q": q_issues, "per_page": 1}
        resp_issues = requests.get(url, headers=core.HEADERS, params=params_issues)
        resp_issues.raise_for_status()
        data_issues = resp_issues.json()
        total_comments += data_issues.get("total_count", 0)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.warning(f"Could not count issue comments (403 Forbidden). Skipping.")
        else:
            logger.error(f"Error counting issue comments: {e}", exc_info=True)
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"Error counting issue comments: {e}", exc_info=True)

    # Count PR comments
    try:
        q_prs = f"repo:{owner}/{repo} type:pr commenter:{username}"
        url = f"{core.GITHUB_API}/search/issues"
        params_prs = {"q": q_prs, "per_page": 1}
        resp_prs = requests.get(url, headers=core.HEADERS, params=params_prs)
        resp_prs.raise_for_status()
        data_prs = resp_prs.json()
        total_comments += data_prs.get("total_count", 0)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.warning(f"Could not count PR comments (403 Forbidden). Skipping.")
        else:
            logger.error(f"Error counting PR comments: {e}", exc_info=True)
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"Error counting PR comments: {e}", exc_info=True)

    return total_comments


def count_lines_of_code(owner, repo, username):
    """
    Count total lines of code added and deleted by a user in commits.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the committer.

    Returns:
        dict: Contains "lines_added" and "lines_deleted" counts.
    """
    commit_list = commits.list_commits(owner, repo, username)
    total_additions = 0
    total_deletions = 0

    if not commit_list:
        return {"lines_added": 0, "lines_deleted": 0}

    for c in commit_list:
        sha = c.get("sha")
        if not sha:
            logger.warning(f"Commit without SHA found. Skipping.")
            continue

        commit_url = f"{core.GITHUB_API}/repos/{owner}/{repo}/commits/{sha}"
        try:
            data = core.paginated_get(commit_url)
            if not data or isinstance(data, list):
                logger.error(f"Error fetching commit details for {sha}.")
                continue

            stats = data.get("stats") or {}
            additions = stats.get("additions", 0)
            deletions = stats.get("deletions", 0)
            total_additions += int(additions)
            total_deletions += int(deletions)
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing commit stats: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error processing commit {sha}: {e}", exc_info=True)

    return {"lines_added": total_additions, "lines_deleted": total_deletions}


def count_images_in_commits(owner, repo, username):
    """
    Count image files in commits made by a user.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the committer.

    Returns:
        int: Total count of image files.
    """
    commit_list = commits.list_commits(owner, repo, username)
    total_images = 0

    if not commit_list:
        return 0

    for c in commit_list:
        sha = c.get("sha")
        if not sha:
            logger.warning(f"Commit without SHA found. Skipping.")
            continue

        commit_url = f"{core.GITHUB_API}/repos/{owner}/{repo}/commits/{sha}"
        try:
            commit_data = core.paginated_get(commit_url)
            if not commit_data or "files" not in commit_data or isinstance(commit_data, list):
                logger.error(f"Error fetching commit files for {sha}.")
                continue

            for file in commit_data["files"]:
                if "filename" in file and any(file["filename"].lower().endswith(ext) for ext in core.IMAGE_EXTENSIONS):
                    total_images += 1
        except Exception as e:
            logger.error(f"Error processing commit files for {sha}: {e}", exc_info=True)

    return total_images
