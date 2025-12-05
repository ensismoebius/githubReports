"""
Extended tests for analyzer module covering edge cases and boundary conditions.
Tests for: Grade boundaries, rounding issues, extreme metrics, justification format
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import pandas as pd
import configparser
import math

from analyzer import analyze_report


class TestAnalyzerExtended(unittest.TestCase):

    def setUp(self):
        """Set up a mock config object before each test."""
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

    # ========== Grade Boundary Tests ==========
    
    def test_grade_boundary_mb_threshold(self):
        """Test score exactly at MB threshold (70)."""
        report_data = {
            "boundary_user": {
                "commits": 35,  # 35*2 = 70
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        self.assertEqual(df[df['username'] == 'boundary_user']['grade'].iloc[0], 'MB')

    def test_grade_boundary_b_threshold(self):
        """Test score exactly at B threshold (40)."""
        report_data = {
            "boundary_user": {
                "commits": 20,  # 20*2 = 40
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        self.assertEqual(df[df['username'] == 'boundary_user']['grade'].iloc[0], 'B')

    def test_grade_boundary_r_threshold(self):
        """Test score exactly at R threshold (15)."""
        report_data = {
            "boundary_user": {
                "commits": 7,  # 7*2 = 14, need 15
                "images_in_commits": 1,  # 1*1 = 1, total = 15
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        self.assertEqual(df[df['username'] == 'boundary_user']['grade'].iloc[0], 'R')

    def test_grade_just_below_mb_threshold(self):
        """Test score just below MB threshold (69)."""
        report_data = {
            "boundary_user": {
                "commits": 9,  # 9*2 = 18, no bonus (threshold is 10)
                "images_in_commits": 51,  # 51*1 = 51, total = 69
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        self.assertEqual(df[df['username'] == 'boundary_user']['grade'].iloc[0], 'B')

    def test_grade_just_above_mb_threshold(self):
        """Test score just above MB threshold (71)."""
        report_data = {
            "boundary_user": {
                "commits": 35,  # 35*2 = 70
                "images_in_commits": 1,  # +1 = 71
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        self.assertEqual(df[df['username'] == 'boundary_user']['grade'].iloc[0], 'MB')

    def test_grade_just_above_b_threshold(self):
        """Test score just above B threshold (41)."""
        report_data = {
            "boundary_user": {
                "commits": 20,  # 20*2 = 40
                "images_in_commits": 1,  # +1 = 41
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        self.assertEqual(df[df['username'] == 'boundary_user']['grade'].iloc[0], 'B')

    # ========== Extreme Metrics Tests ==========
    
    def test_extreme_commits(self):
        """Test with extremely high commit count."""
        report_data = {
            "power_user": {
                "commits": 1000,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        # 1000 * 2 + 20 (bonus) = 2020
        self.assertEqual(df[df['username'] == 'power_user']['total_points'].iloc[0], 2020)

    def test_extreme_lines_of_code(self):
        """Test with extremely high lines of code changes."""
        report_data = {
            "line_master": {
                "commits": 0,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0,
                "lines_added": 100000,
                "lines_deleted": 50000
            }
        }
        
        df = analyze_report(report_data, self.config)
        score = df[df['username'] == 'line_master']['total_points'].iloc[0]
        # total_points should be based on log scale: log10(1 + 150000) * 5
        expected = int(math.floor(math.log10(1 + 150000) * 5))
        self.assertEqual(score, expected)

    def test_extreme_comments(self):
        """Test with extremely high comment count."""
        report_data = {
            "chatty_user": {
                "commits": 0,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 10000
            }
        }
        
        df = analyze_report(report_data, self.config)
        # 10000 * 1 = 10000
        self.assertEqual(df[df['username'] == 'chatty_user']['total_points'].iloc[0], 10000)

    def test_mixed_extreme_metrics(self):
        """Test with multiple high metrics."""
        report_data = {
            "contributor": {
                "commits": 500,
                "images_in_commits": 100,
                "issues_created": 100,
                "issues_resolved_by": 200,
                "prs_opened": 150,
                "prs_with_approvals": 100,
                "comments": 500,
                "lines_added": 50000,
                "lines_deleted": 10000
            }
        }
        
        df = analyze_report(report_data, self.config)
        self.assertGreater(df[df['username'] == 'contributor']['total_points'].iloc[0], 3000)

    # ========== Bonus Threshold Tests ==========
    
    def test_bonus_just_below_threshold(self):
        """Test bonus not applied at 9 commits (threshold is 10)."""
        report_data = {
            "almost_bonus": {
                "commits": 9,  # 9*2 = 18, no bonus
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        # 9*2 = 18
        self.assertEqual(df[df['username'] == 'almost_bonus']['total_points'].iloc[0], 18)

    def test_bonus_at_threshold(self):
        """Test bonus applied exactly at threshold (10 commits)."""
        report_data = {
            "got_bonus": {
                "commits": 10,  # 10*2 = 20, +20 bonus = 40
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        # 10*2 + 20 = 40
        self.assertEqual(df[df['username'] == 'got_bonus']['total_points'].iloc[0], 40)

    def test_bonus_above_threshold(self):
        """Test bonus applied with commits above threshold."""
        report_data = {
            "bonus_user": {
                "commits": 20,  # 20*2 = 40, +20 bonus = 60
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        # 20*2 + 20 = 60
        self.assertEqual(df[df['username'] == 'bonus_user']['total_points'].iloc[0], 60)

    # ========== Log Scale Calculation Tests ==========
    
    def test_lines_of_code_log_calculation(self):
        """Test that log scale calculation is correct for lines."""
        report_data = {
            "log_user": {
                "commits": 0,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0,
                "lines_added": 99,
                "lines_deleted": 1
            }
        }
        
        df = analyze_report(report_data, self.config)
        score = df[df['username'] == 'log_user']['total_points'].iloc[0]
        # log10(1 + 100) * 5 = log10(101) * 5 ≈ 2.004 * 5 ≈ 10
        expected = int(math.floor(math.log10(101) * 5))
        self.assertEqual(score, expected)

    def test_lines_of_code_zero(self):
        """Test that zero score users are excluded from results."""
        report_data = {
            "no_lines": {
                "commits": 0,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0,
                "lines_added": 0,
                "lines_deleted": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        # Users with zero score are excluded, so df should be empty
        self.assertTrue(df.empty)

    # ========== Rounding Tests ==========
    
    def test_rounding_decimal_scores(self):
        """Test that scores with decimals are properly handled."""
        report_data = {
            "rounding_user": {
                "commits": 3,  # 3*2 = 6
                "images_in_commits": 1,  # 1*1 = 1
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0,
                "lines_added": 10,
                "lines_deleted": 5
            }
        }
        
        df = analyze_report(report_data, self.config)
        score = df[df['username'] == 'rounding_user']['total_points'].iloc[0]
        # Should be numeric
        self.assertTrue(isinstance(score, (int, float)) or pd.api.types.is_numeric_dtype(type(score)))

    # ========== Justification Tests ==========
    
    def test_justification_format(self):
        """Test that output has expected columns."""
        report_data = {
            "justified_user": {
                "commits": 5,
                "images_in_commits": 2,
                "issues_created": 1,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        
        # The output should have expected columns
        expected_cols = ['username', 'total_points', 'grade']
        for col in expected_cols:
            self.assertIn(col, df.columns)

    def test_zero_activity_excluded(self):
        """Test that users with zero score and I grade are excluded."""
        report_data = {
            "inactive": {
                "commits": 0,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            },
            "active": {
                "commits": 1,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        # Should only have 'active' user (2 points)
        self.assertEqual(len(df), 1)
        self.assertIn('active', df['username'].values)
        self.assertNotIn('inactive', df['username'].values)

    def test_score_ordering(self):
        """Test that results are ordered by score descending."""
        report_data = {
            "user_low": {
                "commits": 1,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            },
            "user_high": {
                "commits": 50,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            },
            "user_mid": {
                "commits": 10,
                "images_in_commits": 0,
                "issues_created": 0,
                "issues_resolved_by": 0,
                "prs_opened": 0,
                "prs_with_approvals": 0,
                "comments": 0
            }
        }
        
        df = analyze_report(report_data, self.config)
        scores = df['total_points'].tolist()
        # Should be in descending order
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == '__main__':
    unittest.main()
