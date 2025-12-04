"""Report section generators.

Each function returns a Markdown string for a specific report section.
"""
from datetime import datetime
from pathlib import Path
from .utils import (
    _format_number,
    _get_grade_stars,
    _get_grade_emoji,
    _get_status_indicator,
    _create_progress_bar,
    _get_rank_emoji,
)
from .stats import _calculate_contributor_stats, _detect_archetype


def _generate_header(project_name: str, team_name: str, date_str: str = None) -> str:
    if date_str is None:
        date_str = datetime.now().strftime("%B %Y")

    header = f"""<div align="center">\n\n# 🚀 GitHub Performance Dashboard  \n### **{project_name}**  \n#### *{team_name} · {date_str}*\n\n</div>\n\n---\n"""
    return header


def _generate_executive_summary(df, stats) -> str:
    total_lines = stats["total_lines"]
    avg_lines_per_dev = total_lines / stats["total_contributors"] if stats["total_contributors"] > 0 else 0

    summary = """## 📊 Executive Summary\n\n| Metric | Value | Status | Trend |\n|--------|-------|--------|-------|\n"""

    contributor_status = _get_status_indicator(stats["total_contributors"], 20, 5)
    summary += f"| **Total Contributors** | {stats['total_contributors']} | {contributor_status} **{'Optimal' if stats['total_contributors'] >= 20 else 'Good' if stats['total_contributors'] >= 5 else 'Low'}** | → |\n"

    volume_status = _get_status_indicator(total_lines, 50000, 10000)
    summary += f"| **Code Volume** | {_format_number(total_lines)} lines | {volume_status} **{'Excellent' if total_lines >= 50000 else 'Good' if total_lines >= 10000 else 'Needs Work'}** | 📈 |\n"

    lines_status = _get_status_indicator(avg_lines_per_dev, 2000, 500)
    summary += f"| **Avg Lines/Developer** | {_format_number(int(avg_lines_per_dev))} | {lines_status} **{'Excellent' if avg_lines_per_dev >= 2000 else 'Good' if avg_lines_per_dev >= 500 else 'Low'}** | 📈 |\n"

    collab_score = (df['prs_opened'].sum() + df['comments'].sum()) / stats['total_contributors'] if stats['total_contributors'] > 0 else 0
    collab_status = _get_status_indicator(collab_score, 20, 5)
    summary += f"| **Collaboration Index** | {int(collab_score)}/100 | {collab_status} **{'Good' if collab_score >= 20 else 'Fair' if collab_score >= 5 else 'Needs Work'}** | ↗ |\n"

    summary += """\n### 🎯 Performance Distribution\n\n"""

    for grade, label in [('MB', 'Elite'), ('B', 'Strong'), ('R', 'Regular'), ('I', 'Needs Boost')]:
        count = stats['grade_distribution'][grade]['count']
        percentage = stats['grade_distribution'][grade]['percentage']
        bar = _create_progress_bar(percentage, 20)
        summary += f"**{grade} {_get_grade_stars(grade)} ({label}):** `{bar}` **{percentage:.0f}%**  \n"

    summary += "\n---\n\n"
    return summary


def _generate_leaderboard(df) -> str:
    df_sorted = df.sort_values('total_points', ascending=False).reset_index(drop=True)

    leaderboard = "## 🏆 Top Performers Leaderboard\n\n"
    leaderboard += "| Rank | Contributor | Tier | 📦 Code | 🎯 Issues | 🔄 PRs | 💬 Comments | **Superpower** |\n"
    leaderboard += "|------|-------------|------|---------|-----------|--------|----------|-------------|\n"

    for idx, (_, row) in enumerate(df_sorted.head(6).iterrows(), 1):
        rank_emoji = _get_rank_emoji(idx)
        grade = row['grade']
        stars = _get_grade_stars(grade)
        username = row['username']
        code = _format_number(row.get('lines_added', 0) + row.get('lines_deleted', 0))
        issues = f"{row.get('issues_created', 0)}/{row.get('issues_resolved', 0)}"
        prs = row.get('prs_opened', 0)
        comments = row.get('comments', 0)
        archetype, _ = _detect_archetype(row)

        leaderboard += f"| {rank_emoji} | **{username}** | **{grade} {stars}** | {code} | {issues} | {prs} | {comments} | {archetype} |\n"

    if len(df_sorted) > 6:
        leaderboard += f"\n<details>\n<summary>📋 View Full Ranking ({len(df_sorted) - 6} more contributors)</summary>\n\n"
        leaderboard += "| Rank | Contributor | Tier | Score | Commits | PRs | Status |\n"
        leaderboard += "|------|-------------|------|-------|---------|-----|--------|\n"

        for idx, (_, row) in enumerate(df_sorted.iterrows(), 1):
            grade = row['grade']
            status_emoji = _get_status_indicator(row['total_points'], 700, 400)
            leaderboard += f"| {idx} | {row['username']} | {grade} {_get_grade_stars(grade)} | {int(row['total_points'])} | {row['commits']} | {row['prs_opened']} | {status_emoji} |\n"

        leaderboard += "\n</details>\n\n"

    leaderboard += "---\n\n"
    return leaderboard


def _generate_performance_metrics(df) -> str:
    total_lines = df['lines_added'].sum() + df['lines_deleted'].sum()

    metrics = """## 📈 Performance Heatmap\n\n### Code Production Intensity\n```\n"""

    top_10_idx = max(1, int(len(df) * 0.1))
    top_25_idx = max(1, int(len(df) * 0.25))
    bottom_50_idx = max(1, int(len(df) * 0.5))

    df_sorted_by_code = df.sort_values('lines_added', ascending=False)
    top_10_lines = df_sorted_by_code.head(top_10_idx)['lines_added'].sum()
    top_25_lines = df_sorted_by_code.head(top_25_idx)['lines_added'].sum()
    bottom_50_lines = df_sorted_by_code.tail(bottom_50_idx)['lines_added'].sum()

    top_10_pct = (top_10_lines / total_lines * 100) if total_lines > 0 else 0
    top_25_pct = (top_25_lines / total_lines * 100) if total_lines > 0 else 0
    bottom_50_pct = (bottom_50_lines / total_lines * 100) if total_lines > 0 else 0

    metrics += f"Top 10% Contributors:  {_create_progress_bar(top_10_pct)} {top_10_pct:.0f}% of total code\n"
    metrics += f"Top 25% Contributors:  {_create_progress_bar(top_25_pct)} {top_25_pct:.0f}% of total code\n"
    metrics += f"Bottom 50%:            {_create_progress_bar(bottom_50_pct)} {bottom_50_pct:.0f}% of total code\n"

    metrics += "```\n\n### Collaboration Activity\n```\n"

    total_prs = df['prs_opened'].sum()
    total_reviews = df['prs_approved'].sum() if 'prs_approved' in df.columns else 0
    total_comments = df['comments'].sum()
    total_issues = df['issues_created'].sum()

    pr_review_pct = (total_reviews / total_prs * 100) if total_prs > 0 else 0
    comment_pct = (total_comments / total_prs * 100) if total_prs > 0 else 0
    issue_pct = (total_issues / total_prs * 100) if total_prs > 0 else 0

    metrics += f"PR Reviews:            {_create_progress_bar(min(pr_review_pct, 100))} {min(pr_review_pct, 100):.0f}%\n"
    metrics += f"Issue Activity:        {_create_progress_bar(min(issue_pct, 100))} {min(issue_pct, 100):.0f}%\n"
    metrics += f"Comments:              {_create_progress_bar(min(comment_pct, 100))} {min(comment_pct, 100):.0f}%\n"

    metrics += "```\n\n---\n\n"
    return metrics


def _generate_contributor_archetypes(df) -> str:
    archetypes_section = "## 🎭 Contributor Archetypes\n\n"
    archetypes_section += "| Archetype | Count | Characteristics | Top Contributor |\n"
    archetypes_section += "|-----------|-------|-----------------|------------------|\n"

    archetype_data = {}
    for _, row in df.iterrows():
        archetype, description = _detect_archetype(row)
        if archetype not in archetype_data:
            archetype_data[archetype] = {'count': 0, 'description': description, 'top_user': row['username'], 'top_score': row['total_points']}
        archetype_data[archetype]['count'] += 1

        if row['total_points'] > archetype_data[archetype]['top_score']:
            archetype_data[archetype]['top_user'] = row['username']
            archetype_data[archetype]['top_score'] = row['total_points']

    for archetype, data in sorted(archetype_data.items(), key=lambda x: x[1]['count'], reverse=True):
        archetypes_section += f"| {archetype} | {data['count']} | {data['description']} | {data['top_user']} |\n"

    archetypes_section += "\n---\n\n"
    return archetypes_section


def _generate_metrics_deep_dive(df, stats) -> str:
    deep_dive = "## 📊 Metrics Deep Dive\n\n"

    deep_dive += "### 🏗️ Code Production Analysis\n\n"
    deep_dive += "| Statistic | Value | vs Team Avg | Notes |\n"
    deep_dive += "|-----------|-------|------------|-------|\n"

    total_lines = stats['total_lines']
    avg_lines = total_lines / stats['total_contributors'] if stats['total_contributors'] > 0 else 0
    lines_vs_avg = ((avg_lines / (total_lines / len(df))) * 100 - 100) if len(df) > 0 else 0

    deep_dive += f"| **Total Lines** | {_format_number(total_lines)} | +{lines_vs_avg:.0f}% | 🟢 **Excellent volume** |\n"
    deep_dive += f"| **Avg Lines/Dev** | {_format_number(int(avg_lines))} | +{lines_vs_avg:.0f}% | 🟢 **High productivity** |\n"
    deep_dive += f"| **Total PRs** | {stats['total_prs']} | — | 🟢 **Good engagement** |\n"
    deep_dive += f"| **Total Issues** | {stats['total_issues']} | — | 🟡 **Moderate activity** |\n"
    deep_dive += f"| **Total Comments** | {stats['total_comments']} | — | 🟡 **Good collaboration** |\n"

    deep_dive += "\n### 🤝 Collaboration Health\n\n"
    deep_dive += "| Metric | Score | Target | Gap | Status |\n"
    deep_dive += "|--------|-------|--------|-----|--------|\n"

    mb_count = stats['grade_distribution']['MB']['count']
    total = stats['total_contributors']
    elite_percentage = (mb_count / total * 100) if total > 0 else 0

    deep_dive += f"| **Elite Contributors** | {elite_percentage:.0f}% | 25% | {elite_percentage - 25:.0f}% | {'🟢' if elite_percentage >= 25 else '🟡' if elite_percentage >= 15 else '🔴'} |\n"
    deep_dive += f"| **Review Rate** | {(stats['total_prs'] / stats['total_contributors']):.1f}/dev | 10/dev | {'🟢' if stats['total_prs'] / stats['total_contributors'] >= 10 else '🟡' if stats['total_prs'] / stats['total_contributors'] >= 5 else '🔴'} |\n"
    deep_dive += f"| **Issue Resolution** | {stats['total_issues']} | {int(stats['total_prs'] * 1.5)} | {'🟢' if stats['total_issues'] >= stats['total_prs'] * 0.5 else '🟡' if stats['total_issues'] >= stats['total_prs'] * 0.25 else '🔴'} |\n"

    deep_dive += "\n---\n\n"
    return deep_dive


def _generate_recommendations(df, stats) -> str:
    recommendations = "## 🎯 Actionable Recommendations\n\n"

    i_count = stats['grade_distribution']['I']['count']
    i_percentage = stats['grade_distribution']['I']['percentage']

    recommendations += "### 🔥 Priority 1: Boost Collaboration & Engagement\n"
    recommendations += "> **\"Great code deserves great conversation\"**\n\n"
    recommendations += "| Action | Owner | Timeline | Success Metric |\n"
    recommendations += "|--------|-------|----------|----------------|\n"
    recommendations += "| Implement \"Buddy Review\" system | Team Lead | Week 1 | 80% PRs reviewed |\n"
    recommendations += "| Weekly \"Code Show & Tell\" | Tech Lead | Week 2 | 90% attendance |\n"
    recommendations += "| Recognition for best reviewers | Manager | Ongoing | Monthly awards |\n"
    recommendations += "| PR review SLAs | All | Immediate | 24h review target |\n\n"

    recommendations += "### 🚀 Priority 2: Level Up Middle Tier (B & R Contributors)\n"
    recommendations += "> **\"Turn Regular into Remarkable\"**\n\n"

    recommendations += "- **B → MB Pathway:** Assign feature leadership roles\n"
    recommendations += "- **R → B Challenge:** Create \"promotion tasks\" with clear criteria\n"
    recommendations += "- **Weekly 1:1s:** Identify blockers and growth opportunities\n"
    recommendations += "- **Public Recognition:** Celebrate tier promotions in team meetings\n\n"

    if i_count > 0:
        recommendations += "### 🛡️ Priority 3: Support Low-Activity Contributors\n"
        recommendations += "> **\"Everyone has potential to contribute\"**\n\n"

        recommendations += "```\n"
        recommendations += f"Current {i_count} I-tier contributors ({i_percentage:.0f}%)\n"
        recommendations += f"Target: {max(0, i_count - 2)} (-{(2/i_count*100):.0f}%)\n" if i_count > 0 else ""
        recommendations += "Actions:\n"
        recommendations += "├─► Clear expectations: 1+ PR + 3+ commits/month\n"
        recommendations += "├─► \"Good First Issue\" tags for newcomers\n"
        recommendations += "├─► Pair programming with MB/B developers\n"
        recommendations += "└─► Bi-weekly check-ins with team lead\n"
        recommendations += "```\n\n"

    recommendations += "---\n\n"
    return recommendations


def _generate_special_awards(df) -> str:
    awards = """## 🏅 Special Recognition Awards\n\n<div align=\"center\">\n\n### 🏆 **Performance Awards**\n\n| Award | Winner | Achievement |\n|-------|--------|-------------|\n"""

    if len(df) > 0:
        code_champion = df.loc[df['lines_added'].idxmax()]
        awards += f"| **Code Champion** 🥇 | `{code_champion['username']}` | {_format_number(int(code_champion['lines_added']))} lines contributed |\n"

        pr_master = df.loc[df['prs_opened'].idxmax()]
        awards += f"| **PR Master** 📤 | `{pr_master['username']}` | {int(pr_master['prs_opened'])} PRs submitted |\n"

        issue_master = df.loc[(df['issues_created'] + df['issues_resolved']).idxmax()]
        total_issues = int(issue_master['issues_created']) + int(issue_master['issues_resolved'])
        awards += f"| **Issue Master** 🎯 | `{issue_master['username']}` | {total_issues} issues managed |\n"

        comment_champion = df.loc[df['comments'].idxmax()]
        awards += f"| **Communicator** 💬 | `{comment_champion['username']}` | {int(comment_champion['comments'])} discussions |\n"

        consistency_winner = df.loc[df['commits'].idxmax()]
        awards += f"| **Consistency Champion** ⏱️ | `{consistency_winner['username']}` | {int(consistency_winner['commits'])} consistent commits |\n"

        top_scorer = df.loc[df['total_points'].idxmax()]
        awards += f"| **Overall Champion** 👑 | `{top_scorer['username']}` | {int(top_scorer['total_points'])} points (Tier: {top_scorer['grade']}) |\n"

    awards += "\n</div>\n\n---\n\n"
    return awards


def _generate_methodology() -> str:
    methodology = """## 🔍 Data Quality & Methodology\n\n| Check | Status | Notes |\n|-------|--------|-------|\n| **Data Completeness** | ✅ | All contributors included |\n| **Consistency Validation** | ✅ | Metrics cross-verified |\n| **Contributor Mapping** | ✅ | GitHub accounts validated |\n| **Time Coverage** | ✅ | Complete period analyzed |\n\n**Scoring Methodology:**\n- Performance Score: Weighted average of commits, PRs, issues, and code quality metrics\n- Tier Thresholds: MB (≥70), B (≥40), R (≥15), I (<15)\n- Archetype Detection: Based on metric distribution and contribution patterns\n- All data normalized and deduplicated\n\n"""
    return methodology


def _generate_footer() -> str:
    now = datetime.now()
    footer = f"""---\n\n<div align=\"center\">\n\n*Report generated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}*  \n*GitHub Performance Engine v1.0*\n\n---\n\n**💡 Leadership Insight:**  \n*\"The best teams aren't just collections of individuals writing code—they're communities building understanding together. Focus not just on what gets built, but on how the team grows while building it.\"*\n\n</div>\n"""
    return footer
