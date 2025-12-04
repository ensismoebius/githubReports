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
    def _col_sum(column_name: str) -> int:
        return int(df[column_name].sum()) if (len(df) > 0 and column_name in df.columns) else 0

    stats = {
        "total_contributors": len(df),
        "total_commits": _col_sum("commits"),
        "total_lines": _col_sum("lines_added") + _col_sum("lines_deleted"),
        "total_prs": _col_sum("prs_opened"),
        "total_issues": _col_sum("issues_created") + _col_sum("issues_resolved"),
        "total_comments": _col_sum("comments"),
        "total_images": _col_sum("images"),
    }

    grade_counts = df["grade"].value_counts() if len(df) > 0 and "grade" in df.columns else {}
    total = len(df) if len(df) > 0 else 1

    stats["grade_distribution"] = {
        "MB": {"count": int(grade_counts.get("MB", 0)), "percentage": (grade_counts.get("MB", 0) / total * 100) if total > 0 else 0},
        "B": {"count": int(grade_counts.get("B", 0)), "percentage": (grade_counts.get("B", 0) / total * 100) if total > 0 else 0},
        "R": {"count": int(grade_counts.get("R", 0)), "percentage": (grade_counts.get("R", 0) / total * 100) if total > 0 else 0},
        "I": {"count": int(grade_counts.get("I", 0)), "percentage": (grade_counts.get("I", 0) / total * 100) if total > 0 else 0},
    }

    return stats
