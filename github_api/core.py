"""
GitHub API Core Module

Handles core GitHub API functionality including:
- Authentication and configuration
- Paginated requests with rate limit handling
- Error handling utilities

This module contains the foundational functions used by all other API modules.
"""

import time
import requests
import logging

logger = logging.getLogger(__name__)

# Global variables for GitHub API configuration
GITHUB_API = ""
TOKEN = ""
HEADERS = {}
IMAGE_EXTENSIONS = []


def init_github_api(config_obj):
    """
    Initialize global GitHub API settings from a configuration object.

    Args:
        config_obj (ConfigParser): Configuration containing GitHub API settings.
    """
    global GITHUB_API, TOKEN, HEADERS, IMAGE_EXTENSIONS

    GITHUB_API = config_obj['GitHub'].get('ApiUrl', "https://api.github.com")
    TOKEN = config_obj['GitHub'].get('Token')

    HEADERS = {"Accept": "application/vnd.github.v3+json"}
    if TOKEN:
        HEADERS["Authorization"] = f"token {TOKEN}"

    image_ext_str = config_obj['Extensions'].get('Image', '.jpg, .jpeg, .png, .gif, .svg, .bmp, .webp')
    IMAGE_EXTENSIONS = [ext.strip() for ext in image_ext_str.split(',')]
    logger.info("GitHub API initialized successfully.")


def paginated_get(url, params=None):
    """
    Handle paginated GET requests to the GitHub API with rate limit handling.

    Args:
        url (str): The API endpoint URL.
        params (dict, optional): Query parameters. Defaults to None.

    Returns:
        list or dict: Combined results from all pages, or single resource dict.
                      Returns empty list on error.
    """
    params = params or {}
    params.setdefault("per_page", 100)
    page = 1
    results = []

    while True:
        params["page"] = page

        try:
            resp = requests.get(url, headers=HEADERS, params=params)

            # Handle rate limiting
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
                            logger.error("Failed to parse X-RateLimit-Reset header.", exc_info=True)

                    logger.warning(f"Rate limited. Sleeping {wait}s before retrying.")
                    time.sleep(wait + 1)
                    continue

            resp.raise_for_status()
            page_data = resp.json()

            # Handle search API responses (with 'items' key)
            if isinstance(page_data, dict) and 'items' in page_data:
                page_data = page_data.get('items', [])
            # Return single resources directly
            elif not isinstance(page_data, list):
                return page_data

            if not page_data:
                break

            results.extend(page_data)

            if len(page_data) < params["per_page"]:
                break

            page += 1

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for URL: {url} with error: {e}", exc_info=True)
            return []
        except ValueError as e:
            logger.error(f"Failed to decode JSON from response for URL: {url}: {e}", exc_info=True)
            return []

    return results


def _handle_api_error_response(response_data, context_description):
    """
    Extract error message from API error response and log it.

    Args:
        response_data: Response data from API (typically dict with error info).
        context_description (str): Description of operation attempted.

    Returns:
        bool: True if data represents an error, False otherwise.
    """
    if isinstance(response_data, dict):
        error_msg = response_data.get('message', str(response_data))
        logger.error(f"{context_description}: {error_msg}", exc_info=False)
        return True
    return False
