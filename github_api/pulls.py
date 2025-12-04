"""
GitHub API - Pull Request Operations Module

Handles all pull request-related GitHub API operations.
"""

import logging
import requests
from datetime import datetime
from . import core

logger = logging.getLogger(__name__)


def count_prs_opened(owner, repo, username):
    """
    Count total pull requests opened by a specific user in a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the PR creator.

    Returns:
        int: Number of PRs opened. Returns 0 on error.
    """
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url = f"{core.GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}

    try:
        resp = requests.get(url, headers=core.HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("total_count", 0)
    except requests.exceptions.HTTPError as e:
        try:
            error_data = e.response.json()
            if error_data.get("total_count", -1) == 0:
                logger.warning(f"No PRs found for {username} in {owner}/{repo}.")
                return 0
            else:
                logger.error(f"Error counting PRs for {username} in {owner}/{repo}: {e}", exc_info=True)
                return 0
        except (ValueError, TypeError):
            logger.error(f"Error counting PRs for {username} in {owner}/{repo}: {e}", exc_info=True)
            return 0
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"Error counting PRs for {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0


def list_prs_opened(owner, repo, username):
    """
    List all pull requests opened by a specific user in a repository.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the PR creator.

    Returns:
        list: List of PR objects. Returns empty list on error.
    """
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url = f"{core.GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}
    prs = core.paginated_get(url, params=params)

    if isinstance(prs, dict):
        core._handle_api_error_response(prs, f"Error fetching PRs for {username} in {owner}/{repo}")
        return []
    return prs


def get_pr_metrics(owner, repo, username):
    """
    Calculate PR metrics for a user (average merge time and PR size).

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the PR creator.

    Returns:
        dict: Contains "avg_merge_time_seconds" and "avg_pr_size".
    """
    prs = list_prs_opened(owner, repo, username)
    if not prs:
        return {"avg_merge_time_seconds": 0, "avg_pr_size": 0}

    total_merge_time = 0
    merged_prs_count = 0
    total_pr_size = 0

    for pr in prs:
        if pr.get("merged_at"):
            created_at = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
            merged_at = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
            total_merge_time += (merged_at - created_at).total_seconds()
            merged_prs_count += 1

        pr_details_url = pr["pull_request"]["url"]
        try:
            pr_details = core.paginated_get(pr_details_url)
            if pr_details and not isinstance(pr_details, list):
                total_pr_size += pr_details.get("additions", 0) + pr_details.get("deletions", 0)
            elif isinstance(pr_details, list):
                logger.warning(f"Expected single PR details but received list for {pr_details_url}")
        except Exception as e:
            logger.error(f"Error fetching PR details: {e}", exc_info=True)

    avg_merge_time = total_merge_time / merged_prs_count if merged_prs_count > 0 else 0
    avg_pr_size = total_pr_size / len(prs) if prs else 0

    return {"avg_merge_time_seconds": avg_merge_time, "avg_pr_size": avg_pr_size}


def count_prs_approved(owner, repo, username):
    """
    Count PRs opened by user that have at least one approval.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the PR creator.

    Returns:
        int: Number of approved PRs. Returns 0 on error.
    """
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url_search = f"{core.GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}

    try:
        resp = requests.get(url_search, headers=core.HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        approved_count = 0

        for it in items:
            pr_number = it.get("number")
            if not pr_number:
                continue
            reviews_url = f"{core.GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
            reviews = core.paginated_get(reviews_url, params={"per_page": 100})
            if isinstance(reviews, dict):
                error_msg = reviews.get('message', str(reviews))
                logger.error(f"Error fetching reviews for PR #{pr_number}: {error_msg}", exc_info=False)
                continue
            if any((rev.get("state") or "").upper() == "APPROVED" for rev in reviews):
                approved_count += 1
        return approved_count
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"Error counting approved PRs for {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0


def count_pr_reviews(owner, repo, username):
    """
    Count pull requests reviewed by a specific user.

    Args:
        owner (str): Repository owner.
        repo (str): Repository name.
        username (str): GitHub username of the reviewer.

    Returns:
        int: Total count of PRs reviewed. Returns 0 on error.
    """
    q = f"repo:{owner}/{repo} type:pr reviewed-by:{username}"
    url = f"{core.GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 1}

    try:
        resp = requests.get(url, headers=core.HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("total_count", 0)
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"Error counting PR reviews by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0
