"""Statistics and archetype detection for contributors."""
from typing import Dict, Tuple


def _detect_archetype(row) -> Tuple[str, str]:
    """Detect contributor archetype based on contributor metrics.

    Accepts a mapping-like object (pandas Series or dict).
    Returns tuple (archetype_name, description).
    """
    lines = row.get("lines_added", 0) + row.get("lines_deleted", 0)
    images = row.get("images", 0)
    prs = row.get("prs_opened", 0)
    issues = row.get("issues_created", 0)
    commits = row.get("commits", 0)
    comments = row.get("comments", 0)

    if lines > 10000:
        if images > 50:
            return ("🏭 Code Factory", "Massive output contributor")
        else:
            return ("🎨 Asset Architect", "High-volume code producer")
    elif images > 50:
        return ("🎨 Asset Architect", "Rich media contributor")
    elif prs > 15:
        return ("📤 PR Machine", "Prolific PR submitter")
    elif issues > 20 and issues > prs:
        return ("📋 Issue Sheriff", "Issue resolution expert")
    elif comments > 50:
        return ("💬 Communicator", "Team discussion leader")
    elif commits > 30:
        return ("📝 Commit Leader", "Consistent contributor")
    elif lines > 5000:
        return ("🔧 Refactor Master", "Code quality focused")
    else:
        return ("⏱️ Silent Coder", "Low-profile contributor")


def _calculate_contributor_stats(df) -> Dict:
    """Calculate aggregate statistics for report.

    Returns a dict with totals and grade distribution.
    Handles empty DataFrames gracefully.
    """
    stats = {
        "total_contributors": len(df),
        "total_commits": df["commits"].sum() if len(df) > 0 else 0,
        "total_lines": (df["lines_added"].sum() + df["lines_deleted"].sum()) if len(df) > 0 else 0,
        "total_prs": df["prs_opened"].sum() if len(df) > 0 else 0,
        "total_issues": (df["issues_created"].sum() + df["issues_resolved"].sum()) if len(df) > 0 else 0,
        "total_comments": df["comments"].sum() if len(df) > 0 else 0,
        "total_images": df["images"].sum() if len(df) > 0 else 0,
    }

    grade_counts = df["grade"].value_counts() if len(df) > 0 else {}
    total = len(df) if len(df) > 0 else 1

    stats["grade_distribution"] = {
        "MB": {"count": int(grade_counts.get("MB", 0)), "percentage": (grade_counts.get("MB", 0) / total * 100) if total > 0 else 0},
        "B": {"count": int(grade_counts.get("B", 0)), "percentage": (grade_counts.get("B", 0) / total * 100) if total > 0 else 0},
        "R": {"count": int(grade_counts.get("R", 0)), "percentage": (grade_counts.get("R", 0) / total * 100) if total > 0 else 0},
        "I": {"count": int(grade_counts.get("I", 0)), "percentage": (grade_counts.get("I", 0) / total * 100) if total > 0 else 0},
    }

    return stats
