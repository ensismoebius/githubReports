import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock
import configparser
import requests
import logging # Import logging

import github_api

class TestGitHubApi(unittest.TestCase):

    def setUp(self):
        """Set up a mock config object before each test."""
        self.config = configparser.ConfigParser()
        self.config['GitHub'] = {
            'Token': 'test_token',
            'ApiUrl': 'https://api.github.com'
        }
        self.config['Extensions'] = {
            'Image': '.jpg, .png'
        }
        github_api.init_github_api(self.config)

    def test_init_github_api(self):
        """Test that the global API settings are initialized correctly."""
        self.assertEqual(github_api.GITHUB_API, 'https://api.github.com')
        self.assertEqual(github_api.TOKEN, 'test_token')
        self.assertIn('Authorization', github_api.HEADERS)
        self.assertEqual(github_api.HEADERS['Authorization'], 'token test_token')
        self.assertEqual(github_api.IMAGE_EXTENSIONS, ['.jpg', '.png'])

    @patch('github_api.users.requests.get')
    def test_user_exists_true(self, mock_get):
        """Test user_exists returns True when user is found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        self.assertTrue(github_api.user_exists('testuser'))
        mock_get.assert_called_with('https://api.github.com/users/testuser', headers=github_api.HEADERS)

    @patch('github_api.users.requests.get')
    def test_user_exists_false(self, mock_get):
        """Test user_exists returns False when user is not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        self.assertFalse(github_api.user_exists('nonexistentuser'))
        mock_get.assert_called_with('https://api.github.com/users/nonexistentuser', headers=github_api.HEADERS)

    @patch('github_api.users.core.paginated_get')
    def test_get_collaborators(self, mock_paginated_get):
        """Test retrieval of repository collaborators."""
        mock_paginated_get.return_value = [{'login': 'user1'}, {'login': 'user2'}]
        
        collaborators = github_api.get_collaborators('owner', 'repo')
        self.assertEqual(collaborators, ['user1', 'user2'])
        mock_paginated_get.assert_called_with('https://api.github.com/repos/owner/repo/collaborators')

    @patch('github_api.users.core.paginated_get')
    def test_get_collaborators_error(self, mock_paginated_get):
        """Test that get_collaborators returns an empty list on API error."""
        mock_paginated_get.return_value = {"message": "Not Found"}
        collaborators = github_api.get_collaborators('owner', 'repo')
        self.assertEqual(collaborators, [])

    @patch('github_api.commits.core.paginated_get')
    def test_count_commits(self, mock_paginated_get):
        """Test commit counting."""
        mock_paginated_get.return_value = [{}, {}] # Two commit objects
        
        count = github_api.count_commits('owner', 'repo', 'testuser')
        self.assertEqual(count, 2)
        mock_paginated_get.assert_called_with(
            'https://api.github.com/repos/owner/repo/commits',
            params={'author': 'testuser', 'per_page': 100}
        )

    @patch('github_api.issues.requests.get')
    def test_count_issues_created(self, mock_get):
        """Test counting of issues created by a user."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'total_count': 5}
        mock_get.return_value = mock_response

        count = github_api.count_issues_created('owner', 'repo', 'testuser')
        self.assertEqual(count, 5)
        expected_params = {'q': 'repo:owner/repo type:issue author:testuser', 'per_page': 100}
        mock_get.assert_called_with(
            'https://api.github.com/search/issues',
            headers=github_api.HEADERS,
            params=expected_params
        )

    @patch('github_api.pulls.requests.get')
    def test_count_prs_opened(self, mock_get):
        """Test counting of pull requests opened by a user."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'total_count': 3}
        mock_get.return_value = mock_response

        count = github_api.count_prs_opened('owner', 'repo', 'testuser')
        self.assertEqual(count, 3)
        expected_params = {'q': 'repo:owner/repo type:pr author:testuser', 'per_page': 100}
        mock_get.assert_called_with(
            'https://api.github.com/search/issues',
            headers=github_api.HEADERS,
            params=expected_params
        )

    @patch('github_api.pulls.requests.get')
    @patch('github_api.pulls.logger')
    def test_count_prs_opened_http_error_total_count_zero(self, mock_logger, mock_get):
        """
        Test count_prs_opened handles HTTPError with total_count: 0 in response
        by logging a warning and returning 0.
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'total_count': 0}
        # Create an HTTPError instance with the mock_response attached
        http_error = requests.exceptions.HTTPError("Not Found", response=mock_response)
        mock_get.side_effect = http_error

        count = github_api.count_prs_opened('owner', 'repo', 'jujuli2')
        self.assertEqual(count, 0)
        
        # Assert that logger.warning was called
        mock_logger.warning.assert_called_once_with(
            "No PRs found for jujuli2 in owner/repo."
        )
        # Assert that logger.error was NOT called
        mock_logger.error.assert_not_called()

    @patch('github_api.issues.core.paginated_get')
    def test_count_issues_resolved_by(self, mock_paginated_get):
        """Test counting of issues resolved by a user."""
        issues = [
            {'closed_by': {'login': 'testuser'}},
            {'closed_by': {'login': 'anotheruser'}},
            {'closed_by': {'login': 'testuser'}},
            {'pull_request': {}, 'closed_by': {'login': 'testuser'}}, # Should be skipped
            {'closed_by': None}
        ]
        mock_paginated_get.return_value = issues

        count = github_api.count_issues_resolved_by('owner', 'repo', 'testuser')
        self.assertEqual(count, 2)
        mock_paginated_get.assert_called_with(
            'https://api.github.com/repos/owner/repo/issues',
            params={'state': 'closed', 'per_page': 100}
        )

    @patch('github_api.core.requests.get')
    def test_paginated_get_single_page(self, mock_get):
        """Test a paginated GET request that only has one page of results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'id': 1}, {'id': 2}]
        mock_get.return_value = mock_response

        results = github_api.paginated_get('https://api.github.com/some/endpoint')
        self.assertEqual(len(results), 2)
        self.assertEqual(results, [{'id': 1}, {'id': 2}])

    @patch('github_api.core.requests.get')
    def test_paginated_get_multiple_pages(self, mock_get):
        """Test a paginated GET request that has multiple pages."""
        # Simulate two pages of results
        mock_response_page1 = Mock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = [{'id': 1}] * 100 # Full page
        
        mock_response_page2 = Mock()
        mock_response_page2.status_code = 200
        mock_response_page2.json.return_value = [{'id': 2}] * 50 # Partial page
        
        # The last call will return an empty list to terminate the loop
        mock_response_page3 = Mock()
        mock_response_page3.status_code = 200
        mock_response_page3.json.return_value = []

        mock_get.side_effect = [mock_response_page1, mock_response_page2, mock_response_page3]

        results = github_api.paginated_get('https://api.github.com/some/endpoint')
        self.assertEqual(len(results), 150)
        self.assertEqual(mock_get.call_count, 2)

    @patch('github_api.pulls.requests.get')
    def test_count_prs_opened_json_error(self, mock_get):
        """Test count_prs_opened handles JSON decoding errors."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON") # Simulate JSON decode error
        mock_get.return_value = mock_response

        with self.assertLogs('github_api.pulls', level='ERROR') as cm:
            count = github_api.count_prs_opened('owner', 'repo', 'testuser')
            self.assertEqual(count, 0)
            self.assertIn("Error counting PRs", cm.output[0])

    @patch('github_api.core.requests.get')
    @patch('github_api.core.time.sleep', return_value=None)
    def test_paginated_get_rate_limit(self, mock_sleep, mock_get):
        """Test that paginated_get handles rate limiting."""
        mock_rate_limit_response = Mock()
        mock_rate_limit_response.status_code = 403
        mock_rate_limit_response.text = 'rate limit exceeded'
        mock_rate_limit_response.headers = {'Retry-After': '10'}

        mock_success_response = Mock()
        mock_success_response.status_code = 200
        mock_success_response.json.return_value = [{'id': 1}]
        
        mock_get.side_effect = [mock_rate_limit_response, mock_success_response]

        results = github_api.paginated_get('https://api.github.com/some/endpoint')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once_with(11)

if __name__ == '__main__':
    unittest.main()