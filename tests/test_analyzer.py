import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import pandas as pd
import configparser
from analyzer import analyze_report

class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up a mock config and sample report data."""
        self.config = configparser.ConfigParser()
        self.config['Scoring'] = {
            'PointsPerCommit': '2',
            'BonusMbCommitsThreshold': '10',
            'BonusMbPoints': '20',
            'PointsPerImage': '1',
            'PointsPerIssueCreated': '3',
            'PointsPerIssueResolved': '5',
            'PointsPerPrOpened': '4',
            'PointsPerPrApproved': '6',
            'PointsPerComment': '1'
        }
        self.config['Grades'] = {
            'MB': '70',
            'B': '40',
            'R': '15'
        }

        self.report_data = {
            "user1": {
                "commits": 12,
                "images_in_commits": 5,
                "issues_created": 2,
                "issues_resolved_by": 1,
                "prs_opened": 3,
                "prs_with_approvals": 2,
                "comments": 10
            },
            "user2": {
                "commits": 5,
                "images_in_commits": 2,
                "issues_created": 1,
                "issues_resolved_by": 0,
                "prs_opened": 1,
                "prs_with_approvals": 0,
                "comments": 3
            },
            "user3": {
                "error": "User not found"
            }
        }

    def test_analyze_report_structure(self):
        """Test the structure of the output DataFrame."""
        df = analyze_report(self.report_data, self.config)
        
        expected_columns = [
            'Usuário', 'Score', 'Conceito', 'Commits', 'Bônus Commits',
            'Imagens', 'Issues Criadas', 'Issues Resolvidas', 'PRs Abertos',
            'PRs Aprovados', 'Comentários'
        ]
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(list(df.columns), expected_columns)
        self.assertEqual(len(df), 2) # Should exclude user3 with error

    def test_score_calculation(self):
        """Test the score calculation logic."""
        df = analyze_report(self.report_data, self.config)
        
        # --- User1 Score Calculation ---
        # Commits: 12 * 2 = 24
        # Bonus Commits: 20 (since 12 > 10)
        # Images: 5 * 1 = 5
        # Issues Created: 2 * 3 = 6
        # Issues Resolved: 1 * 5 = 5
        # PRs Opened: 3 * 4 = 12
        # PRs Approved: 2 * 6 = 12
        # Comments: 10 * 1 = 10
        # Total Score: 24 + 20 + 5 + 6 + 5 + 12 + 12 + 10 = 94
        user1_score = df[df['Usuário'] == 'user1']['Score'].iloc[0]
        self.assertEqual(user1_score, 94)

        # --- User2 Score Calculation ---
        # Commits: 5 * 2 = 10
        # Bonus Commits: 0 (since 5 < 10)
        # Images: 2 * 1 = 2
        # Issues Created: 1 * 3 = 3
        # Issues Resolved: 0 * 5 = 0
        # PRs Opened: 1 * 4 = 4
        # PRs Approved: 0 * 6 = 0
        # Comments: 3 * 1 = 3
        # Total Score: 10 + 0 + 2 + 3 + 0 + 4 + 0 + 3 = 22
        user2_score = df[df['Usuário'] == 'user2']['Score'].iloc[0]
        self.assertEqual(user2_score, 22)

    def test_grade_assignment(self):
        """Test the grade (Conceito) assignment."""
        df = analyze_report(self.report_data, self.config)
        
        # User1: Score 94 >= 70 -> MB
        user1_grade = df[df['Usuário'] == 'user1']['Conceito'].iloc[0]
        self.assertEqual(user1_grade, 'MB')
        
        # User2: Score 22 >= 15 and < 40 -> R
        user2_grade = df[df['Usuário'] == 'user2']['Conceito'].iloc[0]
        self.assertEqual(user2_grade, 'R')
        
    def test_empty_report(self):
        """Test the analyzer with an empty report."""
        df = analyze_report({}, self.config)
        self.assertTrue(df.empty)

    def test_report_with_only_errors(self):
        """Test the analyzer with a report containing only users with errors."""
        report_with_errors = {
            "user_error_1": {"error": "User not found"},
            "user_error_2": {"commits_error": "API limit"}
        }
        df = analyze_report(report_with_errors, self.config)
        self.assertTrue(df.empty)

    def test_exclude_zero_activity_users(self):
        """Test that users with zero activity (0 score, 'I' grade) are excluded from the report."""
        zero_activity_data = {
            "zero_user": {
                "commits": 0,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            },
            "active_user": {
                "commits": 1,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        df = analyze_report(zero_activity_data, self.config)
        self.assertNotIn('zero_user', df['Usuário'].values)
        self.assertIn('active_user', df['Usuário'].values)


if __name__ == '__main__':
    unittest.main()
