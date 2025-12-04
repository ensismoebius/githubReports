"""Markdown report package.

Expose generate_report and commonly-used helpers so the top-level
`markdown_report_generator.py` can re-export them for backwards compatibility.
"""
from .generator import generate_report
from .loader import load_data
from .stats import _calculate_contributor_stats, _detect_archetype
from .sections import (
    _generate_header,
    _generate_executive_summary,
    _generate_leaderboard,
    _generate_performance_metrics,
    _generate_contributor_archetypes,
    _generate_metrics_deep_dive,
    _generate_recommendations,
    _generate_special_awards,
    _generate_methodology,
    _generate_footer,
)
from .utils import (
    _format_number,
    _get_grade_stars,
    _get_grade_emoji,
    _get_status_indicator,
    _create_progress_bar,
    _get_rank_emoji,
)

__all__ = [
    'generate_report', 'load_data', '_calculate_contributor_stats', '_detect_archetype',
    '_generate_header', '_generate_executive_summary', '_generate_leaderboard',
    '_generate_performance_metrics', '_generate_contributor_archetypes', '_generate_metrics_deep_dive',
    '_generate_recommendations', '_generate_special_awards', '_generate_methodology', '_generate_footer',
    '_format_number', '_get_grade_stars', '_get_grade_emoji', '_get_status_indicator', '_create_progress_bar', '_get_rank_emoji'
]
