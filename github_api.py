
import os # Provides a way of using operating system dependent functionality.

import sys # Provides access to system-specific parameters and functions, used here for stderr.

import time # Provides various time-related functions, used for rate limit handling.

import requests # A popular library for making HTTP requests, used to interact with the GitHub API.

from datetime import datetime # Supplies classes for manipulating dates and times, used for calculating PR merge times.

import logging # Import the logging module



logger = logging.getLogger(__name__)



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

    logger.info("GitHub API initialized successfully.")



def paginated_get(url, params=None):

    """

    Handles paginated GET requests to the GitHub API, including rate limit retries.



    Args:

        url (str): The API endpoint URL to request.

        params (dict, optional): Dictionary of query parameters for the request. Defaults to None.



    Returns:

        list or dict: The combined results from all pages, or a single dictionary if the endpoint

                      does not return a list (e.g., a single resource). Returns an empty list on error.

    """

    params = params or {}

    params.setdefault("per_page", 100) # Set default items per page for pagination.

    page = 1 # Start from the first page.

    results = [] # List to accumulate results from all pages.



    while True:

        params["page"] = page # Set the current page number.

        try:

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

                            logger.error("Failed to parse X-RateLimit-Reset header for wait time.", exc_info=True)

                            wait = 60

                    logger.warning(f"Rate limited. Sleeping {wait}s before retrying URL: {url}")

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

        except requests.exceptions.RequestException as e:

            logger.error(f"Request failed for URL: {url} with error: {e}", exc_info=True)

            return [] # Return empty list on request failure for pagination

        except ValueError as e:

            logger.error(f"Failed to decode JSON from response for URL: {url} with error: {e}", exc_info=True)

            return [] # Return empty list on JSON decode failure

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

        logger.error(f"Error fetching commits for {username} in {owner}/{repo}: {commits.get('message', 'Unknown error')}")

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

        logger.error(f"Error fetching commits for {username} in {owner}/{repo}: {commits.get('message', 'Unknown error')}")

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
    q = f"repo:{owner}/{repo} type:issue author:{username}"
    url = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("total_count", 0)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error counting issues created by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0
    except ValueError as e: # Catch JSON decoding errors
        logger.error(f"Failed to decode JSON from response for issues created by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0

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
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("total_count", 0)
    except requests.exceptions.HTTPError as e:
        try:
            error_data = e.response.json()
            if error_data.get("total_count", -1) == 0:
                logger.warning(f"No PRs found for {username} in {owner}/{repo} (API returned 0 total_count with HTTP error).")
                return 0
            else:
                logger.error(f"Error counting PRs opened by {username} in {owner}/{repo}: {e}", exc_info=True)
                return 0
        except (ValueError, TypeError): # If response can't be parsed as JSON, it's a generic error
            logger.error(f"Error counting PRs opened by {username} in {owner}/{repo}: {e}", exc_info=True)
            return 0
    except requests.exceptions.RequestException as e:
        logger.error(f"Error counting PRs opened by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0
    except ValueError as e: # Catch JSON decoding errors not necessarily from HTTPError response
        logger.error(f"Failed to decode JSON from response for PRs opened by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0

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
    params = {"state": "closed", "per_page": 100}
    issues = paginated_get(url, params=params)
    if isinstance(issues, dict):
        logger.error(f"Error fetching resolved issues for {username} in {owner}/{repo}: {issues.get('message', 'Unknown error')}")
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
    if isinstance(prs, dict):
        logger.error(f"Error fetching PRs opened by {username} in {owner}/{repo}: {prs.get('message', 'Unknown error')}")
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
        if pr.get("merged_at"):
            created_at = datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00"))
            merged_at = datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00"))
            total_merge_time += (merged_at - created_at).total_seconds()
            merged_prs_count += 1
        
        pr_details_url = pr["pull_request"]["url"]
        try:
            pr_details = paginated_get(pr_details_url)
            if pr_details and not isinstance(pr_details, list): # paginated_get can return a dict for single resource
                total_pr_size += pr_details.get("additions", 0) + pr_details.get("deletions", 0)
            elif isinstance(pr_details, list): # This should not happen for a single PR details URL
                logger.warning(f"Expected single PR details but received a list for {pr_details_url}")
        except Exception as e:
            logger.error(f"Error fetching PR details for {pr_details_url}: {e}", exc_info=True)
            # Continue processing other PRs even if one fails

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
    q = f"repo:{owner}/{repo} type:pr author:{username}"
    url_search = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 100}
    try:
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
                logger.error(f"Error fetching reviews for PR #{pr_number} in {owner}/{repo}: {reviews.get('message', 'Unknown error')}")
                continue # Skip this PR but continue with others
            if any((rev.get("state") or "").upper() == "APPROVED" for rev in reviews):
                approved_count += 1
        return approved_count
    except requests.exceptions.RequestException as e:
        logger.error(f"Error counting approved PRs for {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0
    except ValueError as e: # Catch JSON decoding errors
        logger.error(f"Failed to decode JSON from response for approved PRs by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0

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
    q = f"repo:{owner}/{repo} type:pr reviewed-by:{username}"
    url = f"{GITHUB_API}/search/issues"
    params = {"q": q, "per_page": 1}
    try:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("total_count", 0)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error counting PR reviews by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0
    except ValueError as e: # Catch JSON decoding errors
        logger.error(f"Failed to decode JSON from response for PR reviews by {username} in {owner}/{repo}: {e}", exc_info=True)
        return 0

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
    
    try:
        q_issues = f"repo:{owner}/{repo} type:issue commenter:{username}"
        url = f"{GITHUB_API}/search/issues"
        params_issues = {"q": q_issues, "per_page": 1}
        resp_issues = requests.get(url, headers=HEADERS, params=params_issues)
        resp_issues.raise_for_status()
        data_issues = resp_issues.json()
        total_comments += data_issues.get("total_count", 0)
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 403:
            logger.warning(f"Could not count issue comments for user {username} due to a 403 Forbidden error. Skipping.")
        else:
            logger.error(f"Error counting issue comments for {username} in {owner}/{repo}: {e}", exc_info=True)
    except ValueError as e: # Catch JSON decoding errors for issues
        logger.error(f"Failed to decode JSON from response for issue comments by {username} in {owner}/{repo}: {e}", exc_info=True)

    try:
        q_prs = f"repo:{owner}/{repo} type:pr commenter:{username}"
        url = f"{GITHUB_API}/search/issues"
        params_prs = {"q": q_prs, "per_page": 1}
        resp_prs = requests.get(url, headers=HEADERS, params=params_prs)
        resp_prs.raise_for_status()
        data_prs = resp_prs.json()
        total_comments += data_prs.get("total_count", 0)
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 403:
            logger.warning(f"Could not count PR comments for user {username} due to a 403 Forbidden error. Skipping.")
        else:
            logger.error(f"Error counting PR comments for {username} in {owner}/{repo}: {e}", exc_info=True)
    except ValueError as e: # Catch JSON decoding errors for PRs
        logger.error(f"Failed to decode JSON from response for PR comments by {username} in {owner}/{repo}: {e}", exc_info=True)
    
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
        sha = c.get("sha")
        if not sha:
            logger.warning(f"Commit without SHA found for {username} in {owner}/{repo}. Skipping.")
            continue
        commit_url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}"
        try:
            data = paginated_get(commit_url)
            if not data or isinstance(data, list): # Should be single commit detail, not a list
                logger.error(f"Error fetching commit details for {sha} or unexpected data type.")
                continue
            stats = data.get("stats") or {}
            additions = stats.get("additions", 0)
            deletions = stats.get("deletions", 0)
            total_additions += int(additions)
            total_deletions += int(deletions)
        except (ValueError, TypeError) as e:
            logger.error(f"Error processing commit stats for {sha}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing commit {sha}: {e}", exc_info=True)
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
        sha = c.get("sha")
        if not sha:
            logger.warning(f"Commit without SHA found for {username} in {owner}/{repo}. Skipping.")
            continue
        commit_url = f"{GITHUB_API}/repos/{owner}/{repo}/commits/{sha}"
        try:
            commit_data = paginated_get(commit_url)
            if not commit_data or "files" not in commit_data or isinstance(commit_data, list):
                logger.error(f"Error fetching commit files for {sha} or unexpected data type.")
                continue
            for file in commit_data["files"]:
                if "filename" in file and any(file["filename"].lower().endswith(ext) for ext in IMAGE_EXTENSIONS):
                    total_images += 1
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing commit files for {sha}: {e}", exc_info=True)
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
    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 200:
            return True
        if resp.status_code == 404:
            logger.info(f"User {username} does not exist (404 Not Found).")
            return False
        resp.raise_for_status() # For other bad responses
        return False # Should not be reached if raise_for_status works
    except requests.exceptions.RequestException as e:
        logger.error(f"Error checking existence of user {username}: {e}", exc_info=True)
        return False
    except ValueError as e: # Catch JSON decoding errors
        logger.error(f"Failed to decode JSON from response when checking existence of user {username}: {e}", exc_info=True)
        return False

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
    if isinstance(collaborators_data, dict): # paginated_get returns dict with error message on failure
        logger.error(f"Error fetching collaborators for {owner}/{repo}: {collaborators_data.get('message', 'Unknown error')}")
        return []
    elif not isinstance(collaborators_data, list): # unexpected data type
        logger.error(f"Unexpected data type returned for collaborators for {owner}/{repo}.")
        return []
    # Extract the 'login' (username) for each collaborator.
    return [c["login"] for c in collaborators_data]
