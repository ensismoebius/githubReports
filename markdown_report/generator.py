"""Main report orchestration: assemble sections and write the Markdown file.

This module prefers rendering a Jinja2 template when `Jinja2` is
installed. If Jinja2 is not available, it falls back to the original
string-assembly behavior by calling the existing section functions.
"""
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


def _render_with_jinja(context: dict,
                       templates_pkg: str = 'markdown_report',
                       template_name: str = 'report.md.j2',
                       template_path: str | None = None) -> str:
    """Render the report using Jinja2.

    If `template_path` is provided and points to a file, a
    FileSystemLoader is used. Otherwise PackageLoader loads the
    template from the installed `markdown_report` package templates.
    """
    from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
    import os

    if template_path:
        # If a file path was provided, use its directory as loader
        tpl_dir = os.path.dirname(os.path.abspath(template_path)) or '.'
        tpl_name = os.path.basename(template_path)
        loader = FileSystemLoader(tpl_dir)
    else:
        tpl_name = template_name
        loader = PackageLoader(templates_pkg, 'templates')

    from .utils import _format_number, _create_progress_bar, _get_grade_stars, _get_rank_emoji
    from .stats import _detect_archetype

    env = Environment(
        loader=loader,
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
    )

    # Expose some helper functions to templates for formatting
    env.globals.update({
        'format_number': _format_number,
        'progress_bar': _create_progress_bar,
        'grade_stars': _get_grade_stars,
        'rank_emoji': _get_rank_emoji,
        'detect_archetype': _detect_archetype,
    })

    template = env.get_template(tpl_name)
    return template.render(**context)


def generate_report(csv_file_path: str,
                    output_file_path: str,
                    project_name: str = "GitHub Analytics Report",
                    team_name: str = "Development Team",
                    template_path: str | None = None) -> str:
    """Generate a complete Markdown report from CSV data.

    The renderer will attempt to use Jinja2 templates (if installed).
    To keep templates editable by hand, templates are stored under
    `markdown_report/templates/report.md.j2` and may reference the
    rendered section HTML/markdown via the context variables.
    """
    logger.info(f"Starting report generation for {project_name}")

    df = load_data(csv_file_path)
    stats = _calculate_contributor_stats(df)

    # Convert DataFrame to list-of-dicts for template-friendly iteration
    contributors = df.to_dict(orient='records') if len(df) > 0 else []

    # Pre-compute a few convenience metrics for templates
    total_lines = stats.get('total_lines', 0)
    # Code-production percentiles (top 10%, top 25%, bottom 50%) computed by lines_added
    contributors_by_code = sorted(contributors, key=lambda r: r.get('lines_added', 0), reverse=True)
    n = len(contributors_by_code)
    top_10_idx = max(1, int(n * 0.1)) if n > 0 else 0
    top_25_idx = max(1, int(n * 0.25)) if n > 0 else 0
    bottom_50_idx = max(1, int(n * 0.5)) if n > 0 else 0

    top_10_lines = sum(r.get('lines_added', 0) for r in contributors_by_code[:top_10_idx]) if top_10_idx > 0 else 0
    top_25_lines = sum(r.get('lines_added', 0) for r in contributors_by_code[:top_25_idx]) if top_25_idx > 0 else 0
    bottom_50_lines = sum(r.get('lines_added', 0) for r in contributors_by_code[-bottom_50_idx:]) if bottom_50_idx > 0 else 0

    top_10_pct = (top_10_lines / total_lines * 100) if total_lines > 0 else 0
    top_25_pct = (top_25_lines / total_lines * 100) if total_lines > 0 else 0
    bottom_50_pct = (bottom_50_lines / total_lines * 100) if total_lines > 0 else 0

    # Leaderboard helpers
    contributors_by_score = sorted(contributors, key=lambda r: r.get('total_points', 0), reverse=True)
    top_6 = contributors_by_score[:6]

    # Prepare rendering context for templates (data-first; templates should do formatting)
    context = {
        'project_name': project_name,
        'team_name': team_name,
        'contributors': contributors,
        'contributors_by_code': contributors_by_code,
        'contributors_by_score': contributors_by_score,
        'top_6': top_6,
        'stats': stats,
        'total_lines': total_lines,
        'top_10_pct': top_10_pct,
        'top_25_pct': top_25_pct,
        'bottom_50_pct': bottom_50_pct,
    }

    # Try Jinja2 rendering first (supports packaged and filesystem templates),
    # fall back to manual concatenation if Jinja2 is not available or rendering fails.
    try:
        report = _render_with_jinja(context, template_path=template_path)
    except Exception as exc:  # ImportError, TemplateNotFound, or rendering errors -> fallback
        logger.debug("Jinja2 template rendering failed, falling back: %s", exc)
        report = (
            context['header']
            + context['executive_summary']
            + context['leaderboard']
            + context['performance_metrics']
            + context['archetypes']
            + context['deep_dive']
            + context['recommendations']
            + context['awards']
            + context['methodology']
            + context['footer']
        )

    Path(output_file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"Report saved to {output_file_path}")
    return report
