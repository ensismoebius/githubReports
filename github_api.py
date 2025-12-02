
import os
import sys
import time
import requests
from datetime import datetime

# Global variables for GitHub API configuration
GITHUB_API = ""
TOKEN = ""
HEADERS = {}
IMAGE_EXTENSIONS = []

def init_github_api(config_obj):
    global GITHUB_API, TOKEN, HEADERS, IMAGE_EXTENSIONS
    GITHUB_API = config_obj['GitHub'].get('ApiUrl', "https://api.github.com")
    TOKEN = config_obj['GitHub'].get('Token')
    
    HEADERS = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        HEADERS["Authorization"] = f"token {TOKEN}"
    
    image_ext_str = config_obj['Extensions'].get('Image', '.jpg, .jpeg, .png, .gif, .svg, .bmp, .webp')
    IMAGE_EXTENSIONS = [ext.strip() for ext in image_ext_str.split(',')]

def paginated_get(url, params=None):
    params = params or {}
    params.setdefault("per_page", 100)
    page = 1
    results = []
    while True:
        params["page"] = page
        resp = requests.get(url, headers=HEADERS, params=params)
        if resp.status_code == 403:
            response_text = resp.text.lower()
            if "rate limit" in response_text or "secondary rate limit" in response_text:
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    wait = int(retry_after)
                else:
                    reset = resp.headers.get("X-RateLimit-Reset")
                    wait = 60
                    try:
                        wait = max(30, int(reset) - int(time.time()))
                    except Exception:
                        pass
                print(f"[WARN] Rate limited. Sleeping {wait}s...", file=sys.stderr)
                time.sleep(wait + 1)
                continue
        resp.raise_for_status()
        page_data = resp.json()
        if not isinstance(page_data, list):
            return page_data
        if not page_data:
            break
        results.extend(page_data)
        if len(page_data) < params["per_page"]:
            break
        page += 1
    return results

def count_commits(owner, repo, username):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    params = {"author": username, "per_page": 100}
    commits = paginated_get(url, params=params)
    if isinstance(commits, dict):
        return 0
    return len(commits)

def list_commits(owner, repo, username):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    params = {"author": username, "per_page": 100}
    commits = paginated_get(url, params=params)
    if isinstance(commits, dict):
        return []
    return commits

def count_issues_created(owner, repo, username):
    q = f"repo:{owner}/{repo} type:issue author:{username}"
    url = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("total_count", 0)

def count_prs_opened(owner, repo, username):
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("total_count", 0)

def count_issues_resolved_by(owner, repo, username):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
    params = {"state": "closed", "per_page": 100}
    issues = paginated_get(url, params=params)
    if isinstance(issues, dict):
        return 0
    count = 0
    for issue in issues:
        if "pull_request" in issue:
            continue
        closed_by = issue.get("closed_by")
        if closed_by and closed_by.get("login", "").lower() == username.lower():
            count += 1
    return count

def list_prs_opened(owner, repo, username):
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}
    prs = paginated_get(url, params=params)
    if isinstance(prs, dict):
        return []
    return prs

def get_pr_metrics(owner, repo, username):
    prs = list_prs_opened(owner, repo, username)
    if not prs:
        return {"avg_merge_time_seconds": 0, "avg_pr_size": 0}

    total_merge_time = 0
    merged_prs_count = 0
    total_pr_size = 0

    for pr in prs:
        if pr.get("merged_at"):
            created_at = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
            merged_at = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
            total_merge_time += (merged_at - created_at).total_seconds()
            merged_prs_count += 1
        
        # To get additions and deletions, we need to fetch the full PR object
        pr_details_url = pr["pull_request"]["url"]
        pr_details = paginated_get(pr_details_url)
        if pr_details:
            total_pr_size += pr_details.get("additions", 0) + pr_details.get("deletions", 0)

    avg_merge_time = total_merge_time / merged_prs_count if merged_prs_count > 0 else 0
    avg_pr_size = total_pr_size / len(prs) if prs else 0

    return {"avg_merge_time_seconds": avg_merge_time, "avg_pr_size": avg_pr_size}


def count_prs_approved(owner, repo, username):
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url_search = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}
    resp = requests.get(url_search, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("items", [])
    approved_count = 0
    for it in items:
        pr_number = it.get("number")
        if not pr_number:
            continue
        reviews_url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        reviews = paginated_get(reviews_url, params={"per_page": 100})
        if isinstance(reviews, dict):
            reviews = []
        if any((rev.get("state") or "").upper() == "APPROVED" for rev in reviews):
            approved_count += 1
    return approved_count

def count_pr_reviews(owner, repo, username):
    q = f"repo:{owner}/{repo} type:pr reviewed-by:{username}"
    url = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 1} # We only need the total count
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("total_count", 0)

def count_comments(owner, repo, username):
    total_comments = 0
    
    # Count comments on issues
    try:
        q_issues = f"repo:{owner}/{repo} type:issue commenter:{username}"
        url = f"{GITHUB_API}/search/issues"
        params_issues = {"q": q_issues, "per_page": 1}
        resp_issues = requests.get(url, headers=HEADERS, params=params_issues)
        resp_issues.raise_for_status()
        data_issues = resp_issues.json()
        total_comments += data_issues.get("total_count", 0)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"[WARN] Could not count issue comments for user {username} due to a 403 Forbidden error. Skipping.", file=sys.stderr)
        else:
            raise e

    # Count comments on pull requests
    try:
        q_prs = f"repo:{owner}/{repo} type:pr commenter:{username}"
        url = f"{GITHUB_API}/search/issues"
        params_prs = {"q": q_prs, "per_page": 1}
        resp_prs = requests.get(url, headers=HEADERS, params=params_prs)
        resp_prs.raise_for_status()
        data_prs = resp_prs.json()
        total_comments += data_prs.get("total_count", 0)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"[WARN] Could not count PR comments for user {username} due to a 403 Forbidden error. Skipping.", file=sys.stderr)
        else:
            raise e
    
    return total_comments

def count_lines_of_code(owner, repo, username):
    commits = list_commits(owner, repo, username)
    total_additions = 0
    total_deletions = 0
    if not commits:
        return {"lines_added": 0, "lines_deleted": 0}
    for c in commits:
        sha = c.get("sha")
        if not sha:
            continue
        commit_url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}"
        data = paginated_get(commit_url)
        if not data:
            continue
        stats = data.get("stats") or {}
        additions = stats.get("additions", 0)
        deletions = stats.get("deletions", 0)
        try:
            total_additions += int(additions)
            total_deletions += int(deletions)
        except Exception:
            pass
    return {"lines_added": total_additions, "lines_deleted": total_deletions}

def count_images_in_commits(owner, repo, username):
    commits = list_commits(owner, repo, username)
    total_images = 0
    if not commits:
        return 0
    for c in commits:
        sha = c.get("sha")
        if not sha:
            continue
        commit_url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}"
        commit_data = paginated_get(commit_url)
        if not commit_data or "files" not in commit_data:
            continue
        for file in commit_data["files"]:
            if "filename" in file and any(file["filename"].lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                total_images += 1
    return total_images


def user_exists(username):
    url = f"{GITHUB_API}/users/{username}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        return True
    if resp.status_code == 404:
        return False
    resp.raise_for_status()

def get_collaborators(owner, repo):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/collaborators"
    collaborators_data = paginated_get(url)
    if isinstance(collaborators_data, dict):
        return []
    return [c["login"] for c in collaborators_data]
