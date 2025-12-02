
import os # Provides a way of using operating system dependent functionality.
import sys # Provides access to system-specific parameters and functions, used here for stderr.
import time # Provides various time-related functions, used for rate limit handling.
import requests # A popular library for making HTTP requests, used to interact with the GitHub API.
from datetime import datetime # Supplies classes for manipulating dates and times, used for calculating PR merge times.

# Global variables for GitHub API configuration.
# These variables are initialized once and used across all API functions.
GITHUB_API = "" # Base URL for the GitHub API (e.g., https://api.github.com).
TOKEN = "" # Personal Access Token for GitHub API authentication.
HEADERS = {} # HTTP headers to be sent with each API request, including Authorization and Accept.
IMAGE_EXTENSIONS = [] # List of file extensions recognized as images, used for counting images in commits.

def init_github_api(config_obj):
    """
    Initializes global GitHub API settings from a configuration object.

    Args:
        config_obj (ConfigParser): A configuration object containing GitHub API settings.
    """
    global GITHUB_API, TOKEN, HEADERS, IMAGE_EXTENSIONS
    
    # Get the GitHub API URL from the config, or use the default.
    GITHUB_API = config_obj['GitHub'].get('ApiUrl', "https://api.github.com")
    # Get the GitHub Personal Access Token from the config.
    TOKEN = config_obj['GitHub'].get('Token')
    
    # Set standard headers for GitHub API requests.
    HEADERS = {"Accept": "application/vnd.github.v3+json"}
    # If a token is provided, add it to the Authorization header for authenticated requests.
    if TOKEN:
        HEADERS["Authorization"] = f"token {TOKEN}"
    
    # Get image file extensions from the config and parse them into a list.
    image_ext_str = config_obj['Extensions'].get('Image', '.jpg, .jpeg, .png, .gif, .svg, .bmp, .webp')
    IMAGE_EXTENSIONS = [ext.strip() for ext in image_ext_str.split(',')]

def paginated_get(url, params=None):
    """
    Handles paginated GET requests to the GitHub API, including rate limit retries.

    Args:
        url (str): The API endpoint URL to request.
        params (dict, optional): Dictionary of query parameters for the request. Defaults to None.

    Returns:
        list or dict: The combined results from all pages, or a single dictionary if the endpoint
                      does not return a list (e.g., a single resource).
    """
    params = params or {}
    params.setdefault("per_page", 100) # Set default items per page for pagination.
    page = 1 # Start from the first page.
    results = [] # List to accumulate results from all pages.

    while True:
        params["page"] = page # Set the current page number.
        resp = requests.get(url, headers=HEADERS, params=params)
        
        # Handle GitHub API rate limiting (status code 403).
        if resp.status_code == 403:
            response_text = resp.text.lower()
            if "rate limit" in response_text or "secondary rate limit" in response_text:
                retry_after = resp.headers.get("Retry-After") # Time to wait specified by GitHub.
                if retry_after:
                    wait = int(retry_after)
                else:
                    # Calculate wait time based on X-RateLimit-Reset if Retry-After is not present.
                    reset = resp.headers.get("X-RateLimit-Reset")
                    wait = 60 # Default wait if reset header is missing or invalid.
                    try:
                        wait = max(30, int(reset) - int(time.time()))
                    except Exception:
                        pass
                print(f"[WARN] Rate limited. Sleeping {wait}s...", file=sys.stderr)
                time.sleep(wait + 1) # Wait for the specified duration plus a buffer.
                continue # Retry the request after waiting.

        resp.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx).
        page_data = resp.json() # Parse the JSON response.
        
        # If the response is not a list, it means it's a single resource, so return it directly.
        if not isinstance(page_data, list):
            return page_data
        
        # If the page is empty, there are no more results, so break the loop.
        if not page_data:
            break
        
        results.extend(page_data) # Add current page's data to the results list.
        
        # If the number of items received is less than 'per_page', it means it's the last page.
        if len(page_data) < params["per_page"]:
            break
        
        page += 1 # Move to the next page.
    return results

def count_commits(owner, repo, username):
    """
    Counts the total number of commits made by a specific user to a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the author.

    Returns:
        int: The number of commits. Returns 0 if no commits are found or if the API returns an error.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    params = {"author": username, "per_page": 100} # Filter by author and use pagination.
    commits = paginated_get(url, params=params)
    if isinstance(commits, dict): # If the API returns an error or single object instead of list.
        return 0
    return len(commits) # Return the total count of commits.

def list_commits(owner, repo, username):
    """
    Lists all commits made by a specific user to a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the author.

    Returns:
        list: A list of commit objects. Returns an empty list if no commits are found or if the API returns an error.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    params = {"author": username, "per_page": 100} # Filter by author and use pagination.
    commits = paginated_get(url, params=params)
    if isinstance(commits, dict): # If the API returns an error or single object instead of list.
        return []
    return commits # Return the list of commits.

def count_issues_created(owner, repo, username):
    """
    Counts the total number of issues created by a specific user in a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the issue creator.

    Returns:
        int: The number of issues created. Returns 0 if no issues are found.
    """
    # Construct a search query for issues authored by the user in the specified repository.
    q = f"repo:{owner}/{repo} type:issue author:{username}"
    url = f"{GITHUB_API}/search/issues" # GitHub search API endpoint.
    params = {"q": q, "per_page": 100}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status() # Raise an HTTPError for bad responses.
    data = resp.json()
    return data.get("total_count", 0) # Return the total count from the search results.

def count_prs_opened(owner, repo, username):
    """
    Counts the total number of pull requests opened by a specific user in a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the PR creator.

    Returns:
        int: The number of pull requests opened. Returns 0 if no PRs are found.
    """
    # Construct a search query for pull requests authored by the user in the specified repository.
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url = f"{GITHUB_API}/search/issues" # GitHub search API endpoint (PRs are also issues).
    params = {"q": q, "per_page": 100}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status() # Raise an HTTPError for bad responses.
    data = resp.json()
    return data.get("total_count", 0) # Return the total count from the search results.

def count_issues_resolved_by(owner, repo, username):
    """
    Counts the number of issues resolved (closed) by a specific user in a repository.
    This is determined by checking the 'closed_by' field of closed issues.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the user who closed the issues.

    Returns:
        int: The number of issues resolved by the user.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"
    params = {"state": "closed", "per_page": 100} # Get all closed issues.
    issues = paginated_get(url, params=params)
    if isinstance(issues, dict): # Handle cases where API returns error.
        return 0
    count = 0
    for issue in issues:
        # Skip pull requests, as this function is for issues.
        if "pull_request" in issue:
            continue
        closed_by = issue.get("closed_by")
        # Check if the issue was closed by the specified username.
        if closed_by and closed_by.get("login", "").lower() == username.lower():
            count += 1
    return count

def list_prs_opened(owner, repo, username):
    """
    Lists all pull requests opened by a specific user in a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the PR creator.

    Returns:
        list: A list of pull request objects. Returns an empty list if no PRs are found.
    """
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}
    prs = paginated_get(url, params=params)
    if isinstance(prs, dict): # Handle cases where API returns error.
        return []
    return prs

def get_pr_metrics(owner, repo, username):
    """
    Calculates various metrics for pull requests opened by a specific user,
    including average merge time and average PR size.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the PR creator.

    Returns:
        dict: A dictionary containing "avg_merge_time_seconds" and "avg_pr_size".
    """
    prs = list_prs_opened(owner, repo, username)
    if not prs:
        return {"avg_merge_time_seconds": 0, "avg_pr_size": 0}

    total_merge_time = 0
    merged_prs_count = 0
    total_pr_size = 0

    for pr in prs:
        # Calculate merge time for merged PRs.
        if pr.get("merged_at"):
            created_at = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
            merged_at = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
            total_merge_time += (merged_at - created_at).total_seconds()
            merged_prs_count += 1
        
        # To get additions and deletions, we need to fetch the full PR object details.
        # The search API results for PRs do not contain detailed stats like additions/deletions.
        pr_details_url = pr["pull_request"]["url"] # URL to the full PR object.
        pr_details = paginated_get(pr_details_url)
        if pr_details:
            total_pr_size += pr_details.get("additions", 0) + pr_details.get("deletions", 0)

    avg_merge_time = total_merge_time / merged_prs_count if merged_prs_count > 0 else 0
    avg_pr_size = total_pr_size / len(prs) if prs else 0

    return {"avg_merge_time_seconds": avg_merge_time, "avg_pr_size": avg_pr_size}


def count_prs_approved(owner, repo, username):
    """
    Counts the number of pull requests created by a user that have received at least one approval.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the PR creator.

    Returns:
        int: The number of approved pull requests.
    """
    # Search for PRs authored by the user.
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
        # For each PR, fetch its reviews.
        reviews_url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        reviews = paginated_get(reviews_url, params={"per_page": 100})
        if isinstance(reviews, dict): # Handle cases where API returns error.
            reviews = []
        # Check if any review has an 'APPROVED' state.
        if any((rev.get("state") or "").upper() == "APPROVED" for rev in reviews):
            approved_count += 1
    return approved_count

def count_pr_reviews(owner, repo, username):
    """
    Counts the number of pull requests reviewed by a specific user.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the reviewer.

    Returns:
        int: The total count of PRs reviewed by the user.
    """
    # Search for pull requests where the user has provided a review.
    q = f"repo:{owner}/{repo} type:pr reviewed-by:{username}"
    url = f"{GITHUB_API}/search/issues"
    # We only need the total count, so per_page can be 1 to minimize data transfer.
    params = {"q": q, "per_page": 1}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    return data.get("total_count", 0) # Return the total count from the search results.

def count_comments(owner, repo, username):
    """
    Counts the total number of comments made by a specific user on issues and pull requests
    within a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the commenter.

    Returns:
        int: The total count of comments.
    """
    total_comments = 0
    
    # Count comments on issues.
    try:
        q_issues = f"repo:{owner}/{repo} type:issue commenter:{username}"
        url = f"{GITHUB_API}/search/issues"
        params_issues = {"q": q_issues, "per_page": 1}
        resp_issues = requests.get(url, headers=HEADERS, params=params_issues)
        resp_issues.raise_for_status()
        data_issues = resp_issues.json()
        total_comments += data_issues.get("total_count", 0)
    except requests.exceptions.HTTPError as e:
        # Handle 403 Forbidden specifically for rate limiting or permission issues.
        if e.response.status_code == 403:
            print(f"[WARN] Could not count issue comments for user {username} due to a 403 Forbidden error. Skipping.", file=sys.stderr)
        else:
            raise e # Re-raise other HTTP errors.

    # Count comments on pull requests.
    try:
        q_prs = f"repo:{owner}/{repo} type:pr commenter:{username}"
        url = f"{GITHUB_API}/search/issues"
        params_prs = {"q": q_prs, "per_page": 1}
        resp_prs = requests.get(url, headers=HEADERS, params=params_prs)
        resp_prs.raise_for_status()
        data_prs = resp_prs.json()
        total_comments += data_prs.get("total_count", 0)
    except requests.exceptions.HTTPError as e:
        # Handle 403 Forbidden specifically for rate limiting or permission issues.
        if e.response.status_code == 403:
            print(f"[WARN] Could not count PR comments for user {username} due to a 403 Forbidden error. Skipping.", file=sys.stderr)
        else:
            raise e # Re-raise other HTTP errors.
    
    return total_comments

def count_lines_of_code(owner, repo, username):
    """
    Counts the total lines of code added and deleted by a specific user across all their commits
    in a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the committer.

    Returns:
        dict: A dictionary with "lines_added" and "lines_deleted" counts.
    """
    commits = list_commits(owner, repo, username)
    total_additions = 0
    total_deletions = 0
    if not commits:
        return {"lines_added": 0, "lines_deleted": 0}
    
    for c in commits:
        sha = c.get("sha") # Get the SHA hash of the commit.
        if not sha:
            continue
        commit_url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}"
        # Fetch detailed commit information to get stats (additions/deletions).
        data = paginated_get(commit_url)
        if not data:
            continue
        stats = data.get("stats") or {} # Get the 'stats' dictionary, default to empty if not present.
        additions = stats.get("additions", 0)
        deletions = stats.get("deletions", 0)
        try:
            total_additions += int(additions)
            total_deletions += int(deletions)
        except Exception:
            # Safely handle potential type errors if additions/deletions are not integers.
            pass
    return {"lines_added": total_additions, "lines_deleted": total_deletions}

def count_images_in_commits(owner, repo, username):
    """
    Counts the total number of image files (based on predefined extensions)
    included in commits made by a specific user to a repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.
        username (str): The GitHub username of the committer.

    Returns:
        int: The total count of image files.
    """
    commits = list_commits(owner, repo, username)
    total_images = 0
    if not commits:
        return 0
    
    for c in commits:
        sha = c.get("sha") # Get the SHA hash of the commit.
        if not sha:
            continue
        commit_url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}"
        # Fetch detailed commit information to get the list of files changed.
        commit_data = paginated_get(commit_url)
        if not commit_data or "files" not in commit_data:
            continue
        for file in commit_data["files"]:
            # Check if the filename ends with any of the defined image extensions.
            if "filename" in file and any(file["filename"].lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                total_images += 1
    return total_images


def user_exists(username):
    """
    Checks if a given GitHub username corresponds to an existing user.

    Args:
        username (str): The GitHub username to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    url = f"{GITHUB_API}/users/{username}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200: # Status 200 means the user was found.
        return True
    if resp.status_code == 404: # Status 404 means the user was not found.
        return False
    resp.raise_for_status() # Raise an HTTPError for other bad responses.

def get_collaborators(owner, repo):
    """
    Retrieves a list of all collaborators for a given repository.

    Args:
        owner (str): The owner of the repository.
        repo (str): The name of the repository.

    Returns:
        list: A list of GitHub usernames (login) of the collaborators.
              Returns an empty list if no collaborators are found or an error occurs.
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/collaborators"
    collaborators_data = paginated_get(url)
    if isinstance(collaborators_data, dict): # Handle cases where API returns error.
        return []
    # Extract the 'login' (username) for each collaborator.
    return [c["login"] for c in collaborators_data]
