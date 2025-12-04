"""Helper utilities for Markdown report generation.

Contains formatting helpers, progress bars, emojis, and small visual helpers.
"""
from typing import Any


def _format_number(num: Any) -> str:
    """Format numbers with appropriate suffixes (k, M, etc.)."""
    try:
        if isinstance(num, str):
            return num
        num = float(num)
    except Exception:
        return str(num)

    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}k"
    return str(int(num))


def _get_grade_stars(grade: str) -> str:
    stars = {"MB": "⭐⭐⭐⭐", "B": "⭐⭐⭐", "R": "⭐⭐", "I": "⭐"}
    return stars.get(grade, "⭐")


def _get_grade_emoji(grade: str) -> str:
    emojis = {"MB": "🟢", "B": "🟡", "R": "🟠", "I": "🔴"}
    return emojis.get(grade, "⚪")


def _get_status_indicator(value: float, good_threshold: float, bad_threshold: float) -> str:
    """Return a traffic-light emoji for a numeric value."""
    try:
        if value >= good_threshold:
            return "🟢"
        elif value >= bad_threshold:
            return "🟡"
        else:
            return "🔴"
    except Exception:
        return "⚪"


def _create_progress_bar(percentage: float, length: int = 20) -> str:
    """Create a simple Unicode progress bar showing `percentage` over `length` chars."""
    try:
        pct = max(0.0, min(100.0, float(percentage)))
    except Exception:
        pct = 0.0
    filled = int(length * pct / 100)
    return "█" * filled + "░" * (length - filled)


def _get_rank_emoji(rank: int) -> str:
    ranks = {1: "🥇", 2: "🥈", 3: "🥉"}
    return ranks.get(rank, f"{rank}.")
