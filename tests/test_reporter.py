import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from reporter import gather_stats

class TestReporter(unittest.TestCase):

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
    def test_gather_stats_success(self, mock_images, mock_metrics, mock_comments, mock_reviews,
                                  mock_loc, mock_approved, mock_opened, mock_resolved,
                                  mock_created, mock_commits, mock_exists):
        """Test gather_stats for a user with all successful API calls."""
        # --- Mock setup ---
        mock_exists.return_value = True
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

        usernames = ["testuser"]
        repo = "owner/repo"
        
        # --- Call the function ---
        results = gather_stats(repo, usernames)
        
        # --- Assertions ---
        self.assertIn("testuser", results)
        stats = results["testuser"]
        
        self.assertEqual(stats["commits"], 10)
        self.assertEqual(stats["issues_created"], 5)
        self.assertEqual(stats["issues_resolved_by"], 3)
        self.assertEqual(stats["prs_opened"], 4)
        self.assertEqual(stats["prs_with_approvals"], 2)
        self.assertEqual(stats["lines_added"], 100)
        self.assertEqual(stats["lines_deleted"], 20)
        self.assertEqual(stats["pr_reviews"], 6)
        self.assertEqual(stats["comments"], 12)
        self.assertEqual(stats["avg_merge_time_seconds"], 3600)
        self.assertEqual(stats["avg_pr_size"], 150)
        self.assertEqual(stats["images_in_commits"], 7)

    @patch('github_api.user_exists')
    def test_gather_stats_nonexistent_user(self, mock_exists):
        """Test gather_stats for a user that does not exist."""
        mock_exists.return_value = False
        
        usernames = ["nonexistent"]
        repo = "owner/repo"

        results = gather_stats(repo, usernames)
        
        self.assertIn("nonexistent", results)
        self.assertIn("error", results["nonexistent"])
        self.assertEqual(results["nonexistent"]["error"], "User not found")

    @patch('github_api.user_exists')
    @patch('github_api.count_commits')
    @patch('github_api.count_issues_created')
    def test_gather_stats_api_errors(self, mock_created, mock_commits, mock_exists):
        """Test that gather_stats handles exceptions from the API module."""
        mock_exists.return_value = True
        mock_commits.return_value = 10 # Success
        mock_created.side_effect = Exception("API rate limit") # Failure

        usernames = ["erroruser"]
        repo = "owner/repo"

        results = gather_stats(repo, usernames)

        self.assertIn("erroruser", results)
        stats = results["erroruser"]

        # Check for successful call
        self.assertEqual(stats["commits"], 10) 
        
        # Check for error from failed call
        self.assertIn("issues_created_error", stats)
        self.assertEqual(stats["issues_created_error"], "API rate limit")
        
        # Check that other keys (that were not called due to the mocked setup) are not present
        self.assertNotIn("issues_resolved_by", stats)


if __name__ == '__main__':
    unittest.main()
