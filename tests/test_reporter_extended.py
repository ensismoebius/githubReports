"""
Extended tests for reporter module covering helper functions and complex scenarios.
Tests for: _safe_metric_collection, multiple concurrent errors, partial success
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
import logging

from reporter import _safe_metric_collection, gather_stats


class TestReporterExtended(unittest.TestCase):

    @patch('github_api.user_exists')
    def test_safe_metric_collection_success(self, mock_user_exists):
        """Test _safe_metric_collection with successful metric collection."""
        mock_user_exists.return_value = True
        mock_metric_func = MagicMock(return_value=42)
        stats = {}
        
        _safe_metric_collection(
            "test metric",
            mock_metric_func,
            "test_key",
            stats,
            "owner",
            "repo",
            "user1",
            is_dict=False
        )
        
        self.assertEqual(stats["test_key"], 42)
        mock_metric_func.assert_called_with("owner", "repo", "user1")

    @patch('github_api.user_exists')
    def test_safe_metric_collection_error(self, mock_user_exists):
        """Test _safe_metric_collection captures exceptions."""
        mock_user_exists.return_value = True
        mock_metric_func = MagicMock(side_effect=Exception("API Error"))
        stats = {}
        
        _safe_metric_collection(
            "test metric",
            mock_metric_func,
            "test_key",
            stats,
            "owner",
            "repo",
            "user1",
            is_dict=False
        )
        
        self.assertIn("test_key_error", stats)
        self.assertEqual(stats["test_key_error"], "API Error")

    def test_safe_metric_collection_dict_mode(self):
        """Test _safe_metric_collection with is_dict=True."""
        mock_metric_func = MagicMock(return_value={"lines_added": 100, "lines_deleted": 20})
        stats = {}
        
        _safe_metric_collection(
            "lines of code",
            mock_metric_func,
            "loc",
            stats,
            "owner",
            "repo",
            "user1",
            is_dict=True
        )
        
        self.assertEqual(stats["lines_added"], 100)
        self.assertEqual(stats["lines_deleted"], 20)

    def test_safe_metric_collection_dict_mode_error(self):
        """Test _safe_metric_collection dict mode with error."""
        mock_metric_func = MagicMock(side_effect=ValueError("Bad data"))
        stats = {}
        
        _safe_metric_collection(
            "lines of code",
            mock_metric_func,
            "loc",
            stats,
            "owner",
            "repo",
            "user1",
            is_dict=True
        )
        
        self.assertIn("loc_error", stats)

    @patch('github_api.user_exists')
    @patch('github_api.count_commits')
    @patch('github_api.count_issues_created')
    @patch('github_api.count_issues_resolved_by')
    @patch('github_api.count_prs_opened')
    @patch('github_api.count_prs_approved')
    @patch('github_api.count_lines_of_code')
    @patch('github_api.count_pr_reviews')
    @patch('github_api.count_comments')
    @patch('github_api.get_pr_metrics')
    @patch('github_api.count_images_in_commits')
    def test_gather_stats_first_metric_fails(self, mock_images, mock_metrics, mock_comments,
                                             mock_reviews, mock_loc, mock_approved, mock_opened,
                                             mock_resolved, mock_created, mock_commits, mock_exists):
        """Test gather_stats when first metric fails but others succeed."""
        mock_exists.return_value = True
        mock_commits.side_effect = Exception("Commits API down")
        mock_created.return_value = 5
        mock_resolved.return_value = 3
        mock_opened.return_value = 4
        mock_approved.return_value = 2
        mock_loc.return_value = {"lines_added": 100, "lines_deleted": 20}
        mock_reviews.return_value = 6
        mock_comments.return_value = 12
        mock_metrics.return_value = {"avg_merge_time_seconds": 3600, "avg_pr_size": 150}
        mock_images.return_value = 7
        
        results = gather_stats("owner/repo", ["testuser"])
        
        self.assertIn("commits_error", results["testuser"])
        self.assertEqual(results["testuser"]["issues_created"], 5)
        self.assertEqual(results["testuser"]["comments"], 12)

    @patch('github_api.user_exists')
    @patch('github_api.count_commits')
    @patch('github_api.count_issues_created')
    @patch('github_api.count_issues_resolved_by')
    @patch('github_api.count_prs_opened')
    @patch('github_api.count_prs_approved')
    @patch('github_api.count_lines_of_code')
    @patch('github_api.count_pr_reviews')
    @patch('github_api.count_comments')
    @patch('github_api.get_pr_metrics')
    @patch('github_api.count_images_in_commits')
    def test_gather_stats_multiple_failures(self, mock_images, mock_metrics, mock_comments,
                                            mock_reviews, mock_loc, mock_approved, mock_opened,
                                            mock_resolved, mock_created, mock_commits, mock_exists):
        """Test gather_stats when multiple metrics fail."""
        mock_exists.return_value = True
        mock_commits.side_effect = Exception("API down")
        mock_created.side_effect = Exception("API down")
        mock_resolved.return_value = 3
        mock_opened.return_value = 4
        mock_approved.return_value = 2
        mock_loc.return_value = {"lines_added": 0, "lines_deleted": 0}
        mock_reviews.return_value = 0
        mock_comments.side_effect = Exception("API down")
        mock_metrics.return_value = {"avg_merge_time_seconds": 0, "avg_pr_size": 0}
        mock_images.return_value = 0
        
        results = gather_stats("owner/repo", ["testuser"])
        stats = results["testuser"]
        
        self.assertIn("commits_error", stats)
        self.assertIn("issues_created_error", stats)
        self.assertIn("comments_error", stats)
        self.assertEqual(stats["issues_resolved_by"], 3)
        self.assertEqual(stats["prs_opened"], 4)

    @patch('github_api.user_exists')
    @patch('github_api.count_commits')
    @patch('github_api.count_issues_created')
    @patch('github_api.count_issues_resolved_by')
    @patch('github_api.count_prs_opened')
    @patch('github_api.count_prs_approved')
    @patch('github_api.count_lines_of_code')
    @patch('github_api.count_pr_reviews')
    @patch('github_api.count_comments')
    @patch('github_api.get_pr_metrics')
    @patch('github_api.count_images_in_commits')
    def test_gather_stats_multiple_users_mixed_results(self, mock_images, mock_metrics, mock_comments,
                                                       mock_reviews, mock_loc, mock_approved, mock_opened,
                                                       mock_resolved, mock_created, mock_commits, mock_exists):
        """Test gather_stats with multiple users, some failing."""
        # User 1 succeeds
        # User 2 not found
        mock_exists.side_effect = [True, False]
        mock_commits.return_value = 10
        mock_created.return_value = 5
        mock_resolved.return_value = 3
        mock_opened.return_value = 4
        mock_approved.return_value = 2
        mock_loc.return_value = {"lines_added": 100, "lines_deleted": 20}
        mock_reviews.return_value = 6
        mock_comments.return_value = 12
        mock_metrics.return_value = {"avg_merge_time_seconds": 3600, "avg_pr_size": 150}
        mock_images.return_value = 7
        
        results = gather_stats("owner/repo", ["user1", "user2"])
        
        # User 1 has stats
        self.assertEqual(results["user1"]["commits"], 10)
        # User 2 has error
        self.assertIn("error", results["user2"])
        self.assertEqual(results["user2"]["error"], "User not found")

    @patch('github_api.user_exists')
    @patch('github_api.count_commits')
    @patch('github_api.count_issues_created')
    @patch('github_api.count_issues_resolved_by')
    @patch('github_api.count_prs_opened')
    @patch('github_api.count_prs_approved')
    @patch('github_api.count_lines_of_code')
    @patch('github_api.count_pr_reviews')
    @patch('github_api.count_comments')
    @patch('github_api.get_pr_metrics')
    @patch('github_api.count_images_in_commits')
    def test_gather_stats_all_zeros(self, mock_images, mock_metrics, mock_comments,
                                    mock_reviews, mock_loc, mock_approved, mock_opened,
                                    mock_resolved, mock_created, mock_commits, mock_exists):
        """Test gather_stats with user who has no activity."""
        mock_exists.return_value = True
        mock_commits.return_value = 0
        mock_created.return_value = 0
        mock_resolved.return_value = 0
        mock_opened.return_value = 0
        mock_approved.return_value = 0
        mock_loc.return_value = {"lines_added": 0, "lines_deleted": 0}
        mock_reviews.return_value = 0
        mock_comments.return_value = 0
        mock_metrics.return_value = {"avg_merge_time_seconds": 0, "avg_pr_size": 0}
        mock_images.return_value = 0
        
        results = gather_stats("owner/repo", ["inactive_user"])
        stats = results["inactive_user"]
        
        self.assertEqual(stats["commits"], 0)
        self.assertEqual(stats["issues_created"], 0)
        self.assertEqual(stats["comments"], 0)
        self.assertNotIn("error", stats)

    @patch('github_api.user_exists')
    @patch('github_api.count_commits')
    @patch('github_api.count_issues_created')
    @patch('github_api.count_issues_resolved_by')
    @patch('github_api.count_prs_opened')
    @patch('github_api.count_prs_approved')
    @patch('github_api.count_lines_of_code')
    @patch('github_api.count_pr_reviews')
    @patch('github_api.count_comments')
    @patch('github_api.get_pr_metrics')
    @patch('github_api.count_images_in_commits')
    def test_gather_stats_high_activity_user(self, mock_images, mock_metrics, mock_comments,
                                            mock_reviews, mock_loc, mock_approved, mock_opened,
                                            mock_resolved, mock_created, mock_commits, mock_exists):
        """Test gather_stats with highly active user."""
        mock_exists.return_value = True
        mock_commits.return_value = 500
        mock_created.return_value = 50
        mock_resolved.return_value = 100
        mock_opened.return_value = 200
        mock_approved.return_value = 150
        mock_loc.return_value = {"lines_added": 50000, "lines_deleted": 5000}
        mock_reviews.return_value = 300
        mock_comments.return_value = 1000
        mock_metrics.return_value = {"avg_merge_time_seconds": 7200, "avg_pr_size": 250}
        mock_images.return_value = 50
        
        results = gather_stats("owner/repo", ["power_user"])
        stats = results["power_user"]
        
        self.assertEqual(stats["commits"], 500)
        self.assertEqual(stats["issues_created"], 50)
        self.assertEqual(stats["pr_reviews"], 300)
        self.assertEqual(stats["comments"], 1000)
        self.assertNotIn("error", stats)


if __name__ == '__main__':
    unittest.main()
