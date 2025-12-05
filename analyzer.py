
import math
import pandas as pd

def analyze_report(json_data, config):
    """
    Analyzes a GitHub report JSON data, computes scores, and produces a DataFrame with detailed justifications.

    :param json_data: A dictionary loaded from the GitHub report JSON file.
    :param config: The configuration object containing scoring and grading parameters.
    :return: A pandas DataFrame with the analysis results.
    """

    # Scoring parameters from config
    POINTS_PER_COMMIT = int(config['Scoring'].get('PointsPerCommit', 2))
    BONUS_MB_COMMITS_THRESHOLD = int(config['Scoring'].get('BonusMbCommitsThreshold', 19))
    BONUS_MB_POINTS = int(config['Scoring'].get('BonusMbPoints', 20))
    POINTS_PER_IMAGE = int(config['Scoring'].get('PointsPerImage', 4))
    POINTS_PER_ISSUE_CREATED = int(config['Scoring'].get('PointsPerIssueCreated', 1))
    POINTS_PER_ISSUE_RESOLVED = int(config['Scoring'].get('PointsPerIssueResolved', 3))
    POINTS_PER_PR_OPENED = int(config['Scoring'].get('PointsPerPrOpened', 2))
    POINTS_PER_PR_APPROVED = int(config['Scoring'].get('PointsPerPrApproved', 3))
    POINTS_PER_COMMENT = int(config['Scoring'].get('PointsPerComment', 1))

    # Grade thresholds from config
    GRADE_MB_THRESHOLD = int(config['Grades'].get('MB', 70))
    GRADE_B_THRESHOLD = int(config['Grades'].get('B', 40))
    GRADE_R_THRESHOLD = int(config['Grades'].get('R', 15))

    def points_from_lines(added, deleted):
        total = max(0, (added or 0) + (deleted or 0))
        return int(math.floor(math.log10(1 + total) * 5)) if total > 0 else 0

    def grade_from_total(total):
        if total >= GRADE_MB_THRESHOLD:
            return "MB"
        elif total >= GRADE_B_THRESHOLD:
            return "B"
        elif total >= GRADE_R_THRESHOLD:
            return "R"
        else:
            return "I"

    rows = []
    for user, stats in json_data.items():
        if any("error" in key for key in stats.keys()):
            continue

        commits = int(stats.get("commits", 0))
        images = int(stats.get("images_in_commits", 0))
        lines_added = int(stats.get("lines_added", 0))
        lines_deleted = int(stats.get("lines_deleted", 0))
        issues_created = int(stats.get("issues_created", 0))
        issues_resolved = int(stats.get("issues_resolved_by", 0))
        prs_opened = int(stats.get("prs_opened", 0))
        prs_approved = int(stats.get("prs_with_approvals", 0))
        comments = int(stats.get("comments", 0))
        
        # partial scores
        pts_commits = commits * POINTS_PER_COMMIT
        pts_images = images * POINTS_PER_IMAGE
        pts_lines = points_from_lines(lines_added, lines_deleted)
        pts_issues_created = issues_created * POINTS_PER_ISSUE_CREATED
        pts_issues_resolved = issues_resolved * POINTS_PER_ISSUE_RESOLVED
        pts_prs_opened = prs_opened * POINTS_PER_PR_OPENED
        pts_prs_approved = prs_approved * POINTS_PER_PR_APPROVED
        pts_comments = comments * POINTS_PER_COMMENT
        bonus_mb = BONUS_MB_POINTS if commits >= BONUS_MB_COMMITS_THRESHOLD else 0

        total = (pts_commits + pts_images + pts_lines + pts_issues_created +
                 pts_issues_resolved + pts_prs_opened + pts_prs_approved +
                 pts_comments + bonus_mb)
        grade = grade_from_total(total)

        # Build justification comment
        justification_lines = []
        justification_lines.append(f"commits: {commits} → {pts_commits} pts ({POINTS_PER_COMMIT}pt/commit).")
        if bonus_mb:
            justification_lines.append(f"bonus for commits ≥ {BONUS_MB_COMMITS_THRESHOLD}: +{bonus_mb} pts.")
        if images:
            justification_lines.append(f"images: {images} → {pts_images} pts ({POINTS_PER_IMAGE}pt/image).")
        if (lines_added + lines_deleted) > 0:
            justification_lines.append(f"lines changed: {lines_added} added + {lines_deleted} deleted → {pts_lines} pts (log scale).")
        if issues_created:
            justification_lines.append(f"issues created: {issues_created} → {pts_issues_created} pts.")
        if issues_resolved:
            justification_lines.append(f"issues resolved: {issues_resolved} → {pts_issues_resolved} pts.")
        if prs_opened:
            justification_lines.append(f"prs opened: {prs_opened} → {pts_prs_opened} pts.")
        if prs_approved:
            justification_lines.append(f"prs approved: {prs_approved} → {pts_prs_approved} pts.")
        if comments:
            justification_lines.append(f"comments: {comments} → {pts_comments} pts.")
        if not justification_lines:
            justification_lines.append("no measurable contributions → 0 pts.")

        justification = " ".join(justification_lines) + f" total={total} → grade={grade}."

        row = {
            "username": user,
            "commits": commits,
            "images": images,
            "lines_added": lines_added,
            "lines_deleted": lines_deleted,
            "issues_created": issues_created,
            "issues_resolved": issues_resolved,
            "prs_opened": prs_opened,
            "prs_approved": prs_approved,
            "comments": comments,
            "pts_commits": pts_commits,
            "pts_images": pts_images,
            "pts_lines": pts_lines,
            "pts_issues_created": pts_issues_created,
            "pts_issues_resolved": pts_issues_resolved,
            "pts_prs_opened": pts_prs_opened,
            "pts_prs_approved": pts_prs_approved,
            "pts_comments": pts_comments,
            "bonus_mb": bonus_mb,
            "total_points": total,
            "grade": grade,
            "justification": justification
        }
        rows.append(row)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df.sort_values(by="total_points", ascending=False).reset_index(drop=True)
    
    # Filter out users with 0 total points and 'I' grade
    df = df[~((df['total_points'] == 0) & (df['grade'] == 'I'))]
    
    # Rename columns to English for consistency and clarity
    df_renamed = df.rename(columns={
        "username": "username",
        "total_points": "total_points",
        "grade": "grade",
        "commits": "commits",
        "bonus_mb": "bonus_mb",
        "images": "images",
        "issues_created": "issues_created",
        "issues_resolved": "issues_resolved",
        "prs_opened": "prs_opened",
        "prs_approved": "prs_approved",
        "comments": "comments",
        "lines_added": "lines_added",
        "lines_deleted": "lines_deleted",
        "pts_commits": "pts_commits",
        "pts_images": "pts_images",
        "pts_lines": "pts_lines",
        "pts_issues_created": "pts_issues_created",
        "pts_issues_resolved": "pts_issues_resolved",
        "pts_prs_opened": "pts_prs_opened",
        "pts_prs_approved": "pts_prs_approved",
        "pts_comments": "pts_comments",
        "justification": "justification"
    })
    
    # Select and reorder columns - include ALL detailed breakdown columns in English
    final_columns = [
        'username', 'total_points', 'grade', 'commits', 'bonus_mb',
        'images', 'issues_created', 'issues_resolved', 'prs_opened',
        'prs_approved', 'comments',
        'lines_added', 'lines_deleted',
        'pts_commits', 'pts_images', 'pts_lines',
        'pts_issues_created', 'pts_issues_resolved',
        'pts_prs_opened', 'pts_prs_approved', 'pts_comments',
        'justification'
    ]
    
    return df_renamed[final_columns]
