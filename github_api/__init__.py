"""
GitHub API Package

This package provides a comprehensive interface to the GitHub API for collecting
repository and user statistics. It's organized into focused modules:

Modules:
  - core: Core API functionality (init, pagination, error handling)
  - commits: Commit-related operations
  - issues: Issue-related operations
  - pulls: Pull request-related operations
  - metrics: Code metrics and comments
  - users: User and repository operations

All public functions are exposed at the package level for backward compatibility.
"""

import logging
from . import core

logger = logging.getLogger(__name__)

# Expose core module for backward compatibility - access via github_api.core.GITHUB_API
# But for tests that expect github_api.GITHUB_API, we'll use __getattr__
from .core import init_github_api, paginated_get

from .commits import count_commits, list_commits

from .issues import count_issues_created, count_issues_resolved_by

from .pulls import (
    count_prs_opened,
    list_prs_opened,
    get_pr_metrics,
    count_prs_approved,
    count_pr_reviews,
)

from .metrics import (
    count_comments,
    count_lines_of_code,
    count_images_in_commits,
)

from .users import user_exists, get_collaborators

__all__ = [
    # Core
    'init_github_api',
    'paginated_get',
    'logger',
    # Commits
    'count_commits',
    'list_commits',
    # Issues
    'count_issues_created',
    'count_issues_resolved_by',
    # PRs
    'count_prs_opened',
    'list_prs_opened',
    'get_pr_metrics',
    'count_prs_approved',
    'count_pr_reviews',
    # Metrics
    'count_comments',
    'count_lines_of_code',
    'count_images_in_commits',
    # Users
    'user_exists',
    'get_collaborators',
]

# Module-level __getattr__ for backward compatibility with test accessing github_api.GITHUB_API etc
def __getattr__(name):
    """Provide backward compatibility for accessing core module attributes."""
    if name in ('GITHUB_API', 'TOKEN', 'HEADERS', 'IMAGE_EXTENSIONS'):
        return getattr(core, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
