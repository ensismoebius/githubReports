"""Main report orchestration: assemble sections and write the Markdown file."""
from pathlib import Path
import logging
from .loader import load_data
from .stats import _calculate_contributor_stats
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

logger = logging.getLogger(__name__)


def generate_report(csv_file_path: str, output_file_path: str, project_name: str = "GitHub Analytics Report", team_name: str = "Development Team") -> str:
    """Generate a complete Markdown report from CSV data."""
    logger.info(f"Starting report generation for {project_name}")

    df = load_data(csv_file_path)
    stats = _calculate_contributor_stats(df)

    report = _generate_header(project_name, team_name)
    report += _generate_executive_summary(df, stats)
    report += _generate_leaderboard(df)
    report += _generate_performance_metrics(df)
    report += _generate_contributor_archetypes(df)
    report += _generate_metrics_deep_dive(df, stats)
    report += _generate_recommendations(df, stats)
    report += _generate_special_awards(df)
    report += _generate_methodology()
    report += _generate_footer()

    Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"Report saved to {output_file_path}")
    return report
