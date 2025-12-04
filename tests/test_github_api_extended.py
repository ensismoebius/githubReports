"""
Extended tests for github_api module covering additional functions and edge cases.
Tests for: list_commits, list_prs_opened, get_pr_metrics, count_prs_approved,
count_pr_reviews, count_comments, count_lines_of_code, count_images_in_commits
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock
import configparser
import requests

import github_api


class TestGitHubApiExtended(unittest.TestCase):

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

    # ========== list_commits tests ==========
    
    @patch('github_api.commits.core.paginated_get')
    def test_list_commits_success(self, mock_paginated_get):
        """Test listing commits successfully."""
        mock_commits = [
            {'sha': 'abc123', 'message': 'First commit'},
            {'sha': 'def456', 'message': 'Second commit'}
        ]
        mock_paginated_get.return_value = mock_commits
        
        result = github_api.list_commits('owner', 'repo', 'testuser')
        self.assertEqual(result, mock_commits)
        mock_paginated_get.assert_called_with(
            'https://api.github.com/repos/owner/repo/commits',
            params={'author': 'testuser', 'per_page': 100}
        )

    @patch('github_api.commits.core.paginated_get')
    def test_list_commits_error(self, mock_paginated_get):
        """Test list_commits returns empty list on error."""
        mock_paginated_get.return_value = {"message": "Not Found"}
        
        result = github_api.list_commits('owner', 'repo', 'testuser')
        self.assertEqual(result, [])

    @patch('github_api.commits.core.paginated_get')
    def test_list_commits_empty(self, mock_paginated_get):
        """Test list_commits with no commits."""
        mock_paginated_get.return_value = []
        
        result = github_api.list_commits('owner', 'repo', 'testuser')
        self.assertEqual(result, [])

    # ========== list_prs_opened tests ==========
    
    @patch('github_api.pulls.core.paginated_get')
    def test_list_prs_opened_success(self, mock_paginated_get):
        """Test listing PRs opened successfully."""
        mock_prs = [
            {'number': 1, 'title': 'PR 1'},
            {'number': 2, 'title': 'PR 2'}
        ]
        mock_paginated_get.return_value = mock_prs
        
        result = github_api.list_prs_opened('owner', 'repo', 'testuser')
        self.assertEqual(result, mock_prs)

    @patch('github_api.pulls.core.paginated_get')
    def test_list_prs_opened_error(self, mock_paginated_get):
        """Test list_prs_opened returns empty list on error."""
        mock_paginated_get.return_value = {"message": "Not Found"}
        
        result = github_api.list_prs_opened('owner', 'repo', 'testuser')
        self.assertEqual(result, [])

    @patch('github_api.pulls.core.paginated_get')
    def test_list_prs_opened_empty(self, mock_paginated_get):
        """Test list_prs_opened with no PRs."""
        mock_paginated_get.return_value = []
        
        result = github_api.list_prs_opened('owner', 'repo', 'testuser')
        self.assertEqual(result, [])

    # ========== get_pr_metrics tests ==========
    
    @patch('github_api.pulls.list_prs_opened')
    def test_get_pr_metrics_no_prs(self, mock_list_prs):
        """Test get_pr_metrics with no PRs returns zeros."""
        mock_list_prs.return_value = []
        
        metrics = github_api.get_pr_metrics('owner', 'repo', 'testuser')
        self.assertEqual(metrics['avg_merge_time_seconds'], 0)
        self.assertEqual(metrics['avg_pr_size'], 0)

    @patch('github_api.pulls.core.paginated_get')
    @patch('github_api.pulls.list_prs_opened')
    def test_get_pr_metrics_unmerged_prs(self, mock_list_prs, mock_paginated_get):
        """Test get_pr_metrics with unmerged PRs."""
        mock_prs = [
            {
                'number': 1,
                'created_at': '2024-01-01T00:00:00Z',
                'merged_at': None,
                'pull_request': {'url': 'https://api.github.com/repos/owner/repo/pulls/1'}
            }
        ]
        mock_list_prs.return_value = mock_prs
        mock_paginated_get.return_value = {
            'additions': 50,
            'deletions': 10
        }
        
        metrics = github_api.get_pr_metrics('owner', 'repo', 'testuser')
        # Unmerged PRs contribute to size but not merge time
        self.assertEqual(metrics['avg_merge_time_seconds'], 0)
        self.assertEqual(metrics['avg_pr_size'], 60)

    @patch('github_api.pulls.core.paginated_get')
    @patch('github_api.pulls.list_prs_opened')
    def test_get_pr_metrics_merged_pr(self, mock_list_prs, mock_paginated_get):
        """Test get_pr_metrics with merged PRs."""
        mock_prs = [
            {
                'number': 1,
                'created_at': '2024-01-01T00:00:00Z',
                'merged_at': '2024-01-02T00:00:00Z',
                'pull_request': {'url': 'https://api.github.com/repos/owner/repo/pulls/1'}
            }
        ]
        mock_list_prs.return_value = mock_prs
        mock_paginated_get.return_value = {
            'additions': 100,
            'deletions': 50
        }
        
        metrics = github_api.get_pr_metrics('owner', 'repo', 'testuser')
        # 1 day = 86400 seconds
        self.assertGreater(metrics['avg_merge_time_seconds'], 0)
        self.assertEqual(metrics['avg_pr_size'], 150)

    # ========== count_prs_approved tests ==========
    
    @patch('github_api.pulls.requests.get')
    def test_count_prs_approved_no_prs(self, mock_get):
        """Test count_prs_approved with no PRs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response
        
        count = github_api.count_prs_approved('owner', 'repo', 'testuser')
        self.assertEqual(count, 0)

    @patch('github_api.pulls.core.paginated_get')
    @patch('github_api.pulls.requests.get')
    def test_count_prs_approved_with_approvals(self, mock_get, mock_paginated_get):
        """Test count_prs_approved counts PRs with APPROVED reviews."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'number': 1},
                {'number': 2}
            ]
        }
        mock_get.return_value = mock_response
        
        # First PR has approval, second doesn't
        mock_paginated_get.side_effect = [
            [{'state': 'APPROVED'}],
            [{'state': 'COMMENTED'}]
        ]
        
        count = github_api.count_prs_approved('owner', 'repo', 'testuser')
        self.assertEqual(count, 1)

    @patch('github_api.pulls.requests.get')
    def test_count_prs_approved_http_error(self, mock_get):
        """Test count_prs_approved handles HTTP errors."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        count = github_api.count_prs_approved('owner', 'repo', 'testuser')
        self.assertEqual(count, 0)

    # ========== count_pr_reviews tests ==========
    
    @patch('github_api.pulls.requests.get')
    def test_count_pr_reviews_success(self, mock_get):
        """Test count_pr_reviews returns review count."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'total_count': 5}
        mock_get.return_value = mock_response
        
        count = github_api.count_pr_reviews('owner', 'repo', 'testuser')
        self.assertEqual(count, 5)

    @patch('github_api.pulls.requests.get')
    def test_count_pr_reviews_zero(self, mock_get):
        """Test count_pr_reviews with no reviews."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'total_count': 0}
        mock_get.return_value = mock_response
        
        count = github_api.count_pr_reviews('owner', 'repo', 'testuser')
        self.assertEqual(count, 0)

    @patch('github_api.pulls.requests.get')
    def test_count_pr_reviews_http_error(self, mock_get):
        """Test count_pr_reviews handles HTTP errors."""
        mock_get.side_effect = requests.exceptions.RequestException("API error")
        
        count = github_api.count_pr_reviews('owner', 'repo', 'testuser')
        self.assertEqual(count, 0)

    # ========== count_comments tests ==========
    
    @patch('github_api.metrics.requests.get')
    def test_count_comments_success(self, mock_get):
        """Test count_comments counts issue and PR comments."""
        mock_response_issues = Mock()
        mock_response_issues.status_code = 200
        mock_response_issues.json.return_value = {'total_count': 3}
        
        mock_response_prs = Mock()
        mock_response_prs.status_code = 200
        mock_response_prs.json.return_value = {'total_count': 2}
        
        mock_get.side_effect = [mock_response_issues, mock_response_prs]
        
        count = github_api.count_comments('owner', 'repo', 'testuser')
        self.assertEqual(count, 5)

    @patch('github_api.metrics.requests.get')
    def test_count_comments_only_issues(self, mock_get):
        """Test count_comments with only issue comments."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'total_count': 4}
        
        mock_response_403 = Mock()
        mock_response_403.status_code = 403
        mock_response_403.text = 'rate limit exceeded'
        
        http_error = requests.exceptions.HTTPError(response=mock_response_403)
        
        mock_get.side_effect = [
            mock_response,
            http_error
        ]
        
        count = github_api.count_comments('owner', 'repo', 'testuser')
        self.assertEqual(count, 4)

    @patch('github_api.metrics.requests.get')
    def test_count_comments_http_error_403(self, mock_get):
        """Test count_comments handles 403 errors gracefully."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = 'rate limit exceeded'
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        count = github_api.count_comments('owner', 'repo', 'testuser')
        self.assertEqual(count, 0)

    # ========== count_lines_of_code tests ==========
    
    @patch('github_api.metrics.core.paginated_get')
    @patch('github_api.metrics.commits.list_commits')
    def test_count_lines_of_code_no_commits(self, mock_list_commits, mock_paginated_get):
        """Test count_lines_of_code with no commits."""
        mock_list_commits.return_value = []
        
        result = github_api.count_lines_of_code('owner', 'repo', 'testuser')
        self.assertEqual(result['lines_added'], 0)
        self.assertEqual(result['lines_deleted'], 0)

    @patch('github_api.metrics.core.paginated_get')
    @patch('github_api.metrics.commits.list_commits')
    def test_count_lines_of_code_with_commits(self, mock_list_commits, mock_paginated_get):
        """Test count_lines_of_code counts additions and deletions."""
        mock_list_commits.return_value = [
            {'sha': 'abc123'},
            {'sha': 'def456'}
        ]
        mock_paginated_get.side_effect = [
            {'stats': {'additions': 100, 'deletions': 20}},
            {'stats': {'additions': 50, 'deletions': 10}}
        ]
        
        result = github_api.count_lines_of_code('owner', 'repo', 'testuser')
        self.assertEqual(result['lines_added'], 150)
        self.assertEqual(result['lines_deleted'], 30)

    @patch('github_api.metrics.core.paginated_get')
    @patch('github_api.metrics.commits.list_commits')
    def test_count_lines_of_code_missing_stats(self, mock_list_commits, mock_paginated_get):
        """Test count_lines_of_code handles commits with missing stats."""
        mock_list_commits.return_value = [
            {'sha': 'abc123'},
            {'sha': 'def456'}
        ]
        mock_paginated_get.side_effect = [
            {'stats': {'additions': 100, 'deletions': 20}},
            {}  # Missing stats
        ]
        
        result = github_api.count_lines_of_code('owner', 'repo', 'testuser')
        self.assertEqual(result['lines_added'], 100)
        self.assertEqual(result['lines_deleted'], 20)

    # ========== count_images_in_commits tests ==========
    
    @patch('github_api.metrics.core.paginated_get')
    @patch('github_api.metrics.commits.list_commits')
    def test_count_images_in_commits_no_commits(self, mock_list_commits, mock_paginated_get):
        """Test count_images_in_commits with no commits."""
        mock_list_commits.return_value = []
        
        count = github_api.count_images_in_commits('owner', 'repo', 'testuser')
        self.assertEqual(count, 0)

    @patch('github_api.metrics.core.paginated_get')
    @patch('github_api.metrics.commits.list_commits')
    def test_count_images_in_commits_with_images(self, mock_list_commits, mock_paginated_get):
        """Test count_images_in_commits counts image files."""
        mock_list_commits.return_value = [
            {'sha': 'abc123'},
            {'sha': 'def456'}
        ]
        mock_paginated_get.side_effect = [
            {
                'files': [
                    {'filename': 'image.jpg'},
                    {'filename': 'photo.png'},
                    {'filename': 'code.py'}
                ]
            },
            {
                'files': [
                    {'filename': 'diagram.png'}
                ]
            }
        ]
        
        count = github_api.count_images_in_commits('owner', 'repo', 'testuser')
        self.assertEqual(count, 3)

    @patch('github_api.metrics.core.paginated_get')
    @patch('github_api.metrics.commits.list_commits')
    def test_count_images_in_commits_no_images(self, mock_list_commits, mock_paginated_get):
        """Test count_images_in_commits with no image files."""
        mock_list_commits.return_value = [{'sha': 'abc123'}]
        mock_paginated_get.return_value = {
            'files': [
                {'filename': 'code.py'},
                {'filename': 'script.js'}
            ]
        }
        
        count = github_api.count_images_in_commits('owner', 'repo', 'testuser')
        self.assertEqual(count, 0)

    @patch('github_api.metrics.core.paginated_get')
    @patch('github_api.metrics.commits.list_commits')
    def test_count_images_in_commits_missing_files(self, mock_list_commits, mock_paginated_get):
        """Test count_images_in_commits handles commits with no files key."""
        mock_list_commits.return_value = [{'sha': 'abc123'}]
        mock_paginated_get.return_value = {'stats': {'additions': 10}}  # No 'files' key
        
        count = github_api.count_images_in_commits('owner', 'repo', 'testuser')
        self.assertEqual(count, 0)


if __name__ == '__main__':
    unittest.main()
