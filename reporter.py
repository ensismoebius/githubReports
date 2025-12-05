"""
Reporter Module

This module is responsible for gathering GitHub statistics for users in a repository.
It collects metrics such as commits, PRs, issues, code reviews, and other GitHub activity
indicators using the GitHub API.

Functions:
    gather_stats: Main function to collect all statistics for specified users.
    _safe_metric_collection: Helper function to safely collect individual metrics with error handling.
"""

import logging
from tqdm import tqdm
import github_api

logger = logging.getLogger(__name__)

def _safe_metric_collection(metric_name, metric_func, stat_key, stats, owner, repo, user, is_dict=False):
    """
    Safely collect a metric with error handling and logging.
    
    Args:
        metric_name (str): Human-readable name of the metric for logging.
        metric_func (callable): Function to call to collect the metric.
        stat_key (str): Key to store the metric in stats dict.
        stats (dict): Dictionary to store the metric result.
        owner (str): Repository owner.
        repo (str): Repository name.
        user (str): GitHub username.
        is_dict (bool): If True, update stats dict; if False, set single value.
    """
    try:
        logger.debug(f"  Collecting {metric_name} for {user}...")
        result = metric_func(owner, repo, user)
        if is_dict:
            stats.update(result)
            if isinstance(result, dict) and 'lines_added' in result:
                logger.debug(f"  Finished collecting {metric_name} for {user}: {result.get('lines_added', 0)} added, {result.get('lines_deleted', 0)} deleted.")
            else:
                logger.debug(f"  Finished collecting {metric_name} for {user}.")
        else:
            stats[stat_key] = result
            logger.debug(f"  Finished collecting {metric_name} for {user}: {result}.")
    except Exception as e:
        error_key = f"{stat_key}_error" if not is_dict else f"{stat_key}_error"
        stats[error_key] = str(e)
        logger.error(f"  Error collecting {metric_name} for {user}: {e}", exc_info=True)

def gather_stats(owner_repo, usernames):
    """
    Gather GitHub statistics for multiple users in a repository.
    
    Args:
        owner_repo (str): Repository in format 'owner/repo'.
        usernames (list): List of GitHub usernames to gather stats for.
        
    Returns:
        dict: Dictionary with user stats keyed by username.
    """
    owner, repo = owner_repo.split("/", 1)
    results = {}
    logger.info(f"Gathering statistics for {len(usernames)} users in {owner_repo}...")
    
    for user in tqdm(usernames, desc="Gathering GitHub stats"):
        stats = {}
        logger.debug(f"Processing user: {user}")

        if not github_api.user_exists(user):
            logger.warning(f"User '{user}' not found on GitHub. Skipping.")
            stats["error"] = "User not found"
            results[user] = stats
            continue
        
        # Collect all metrics for the user
        _safe_metric_collection("commits", github_api.count_commits, "commits", stats, owner, repo, user)
        _safe_metric_collection("issues created", github_api.count_issues_created, "issues_created", stats, owner, repo, user)
        _safe_metric_collection("issues resolved", github_api.count_issues_resolved_by, "issues_resolved_by", stats, owner, repo, user)
        _safe_metric_collection("PRs opened", github_api.count_prs_opened, "prs_opened", stats, owner, repo, user)
        _safe_metric_collection("PRs with approvals", github_api.count_prs_approved, "prs_with_approvals", stats, owner, repo, user)
        _safe_metric_collection("lines of code", github_api.count_lines_of_code, "lines_of_code", stats, owner, repo, user, is_dict=True)
        _safe_metric_collection("PR reviews", github_api.count_pr_reviews, "pr_reviews", stats, owner, repo, user)
        _safe_metric_collection("comments", github_api.count_comments, "comments", stats, owner, repo, user)
        _safe_metric_collection("PR metrics", github_api.get_pr_metrics, "pr_metrics", stats, owner, repo, user, is_dict=True)
        _safe_metric_collection("images in commits", github_api.count_images_in_commits, "images_in_commits", stats, owner, repo, user)
        
        results[user] = stats
    
    return results
