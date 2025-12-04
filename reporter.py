
from tqdm import tqdm
import github_api

def gather_stats(owner_repo, usernames):
    owner, repo = owner_repo.split("/", 1)
    results = {}
    print(f"Gathering statistics for {len(usernames)} users in {owner_repo}...")
    for user in tqdm(usernames, desc="Processing users"):
        stats = {}
        tqdm.write(f"  Processing user: {user}")

        if not github_api.user_exists(user):
            tqdm.write(f"  [WARN] User '{user}' not found on GitHub. Skipping.")
            stats["error"] = "User not found"
            results[user] = stats
            continue
        try:
            tqdm.write(f"    Counting commits for {user}...")
            commits_count = github_api.count_commits(owner, repo, user)
            stats["commits"] = commits_count
            tqdm.write(f"    Finished counting commits for {user}: {commits_count} commits.")
        except Exception as e:
            stats["commits_error"] = str(e)
            tqdm.write(f"    Error counting commits for {user}: {str(e)}")
        try:
            tqdm.write(f"    Counting issues created by {user}...")
            issues_created_count = github_api.count_issues_created(owner, repo, user)
            stats["issues_created"] = issues_created_count
            tqdm.write(f"    Finished counting issues created by {user}: {issues_created_count} issues.")
        except Exception as e:
            stats["issues_created_error"] = str(e)
            tqdm.write(f"    Error counting issues created by {user}: {str(e)}")
        try:
            tqdm.write(f"    Counting issues resolved by {user}...")
            issues_resolved_count = github_api.count_issues_resolved_by(owner, repo, user)
            stats["issues_resolved_by"] = issues_resolved_count
            tqdm.write(f"    Finished counting issues resolved by {user}: {issues_resolved_count} issues.")
        except Exception as e:
            stats["issues_resolved_by_error"] = str(e)
            tqdm.write(f"    Error counting issues resolved by {user}: {str(e)}")
        try:
            tqdm.write(f"    Counting PRs opened by {user}...")
            prs_opened_count = github_api.count_prs_opened(owner, repo, user)
            stats["prs_opened"] = prs_opened_count
            tqdm.write(f"    Finished counting PRs opened by {user}: {prs_opened_count} PRs.")
        except Exception as e:
            stats["prs_opened_error"] = str(e)
            tqdm.write(f"    Error counting PRs opened by {user}: {str(e)}")
        try:
            tqdm.write(f"    Counting PRs with approvals for {user}...")
            prs_approved_count = github_api.count_prs_approved(owner, repo, user)
            stats["prs_with_approvals"] = prs_approved_count
            tqdm.write(f"    Finished counting PRs with approvals for {user}: {prs_approved_count} PRs.")
        except Exception as e:
            stats["prs_with_approvals_error"] = str(e)
            tqdm.write(f"    Error counting PRs with approvals for {user}: {str(e)}")
        try:
            tqdm.write(f"    Counting lines of code for {user}...")
            lines_of_code = github_api.count_lines_of_code(owner, repo, user)
            stats.update(lines_of_code)
            tqdm.write(f"    Finished counting lines of code for {user}: {lines_of_code['lines_added']} added, {lines_of_code['lines_deleted']} deleted.")
        except Exception as e:
            stats["lines_of_code_error"] = str(e)
            tqdm.write(f"    Error counting lines of code for {user}: {str(e)}")
        try:
            tqdm.write(f"    Counting PR reviews for {user}...")
            pr_reviews_count = github_api.count_pr_reviews(owner, repo, user)
            stats["pr_reviews"] = pr_reviews_count
            tqdm.write(f"    Finished counting PR reviews for {user}: {pr_reviews_count} reviews.")
        except Exception as e:
            stats["pr_reviews_error"] = str(e)
            tqdm.write(f"    Error counting PR reviews for {user}: {str(e)}")
        try:
            tqdm.write(f"    Counting comments for {user}...")
            comments_count = github_api.count_comments(owner, repo, user)
            stats["comments"] = comments_count
            tqdm.write(f"    Finished counting comments for {user}: {comments_count} comments.")
        except Exception as e:
            stats["comments_error"] = str(e)
            tqdm.write(f"    Error counting comments for {user}: {str(e)}")
        try:
            tqdm.write(f"    Calculating PR metrics for {user}...")
            pr_metrics = github_api.get_pr_metrics(owner, repo, user)
            stats.update(pr_metrics)
            tqdm.write(f"    Finished calculating PR metrics for {user}.")
        except Exception as e:
            stats["pr_metrics_error"] = str(e)
            tqdm.write(f"    Error calculating PR metrics for {user}: {str(e)}")
        try:
            tqdm.write(f"    Counting images in commits for {user}...")
            images_in_commits_count = github_api.count_images_in_commits(owner, repo, user)
            stats["images_in_commits"] = images_in_commits_count
            tqdm.write(f"    Finished counting images in commits for {user}: {images_in_commits_count} images.")
        except Exception as e:
            stats["images_in_commits_error"] = str(e)
            tqdm.write(f"    Error counting images in commits for {user}: {str(e)}")
        results[user] = stats
    return results
