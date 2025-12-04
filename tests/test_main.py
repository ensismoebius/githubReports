import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock, mock_open
import argparse
import pandas as pd
from main import main

class TestMain(unittest.TestCase):

    @patch('argparse.ArgumentParser.parse_args')
    @patch('main.get_config')
    @patch('main.github_api')
    @patch('main.reporter')
    @patch('main.analyzer')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_main_all_collaborators_json(self, mock_json_dump, mock_file, mock_analyzer, mock_reporter, mock_github_api, mock_get_config, mock_parse_args):
        """Test the main function with --all-collaborators and --json flags."""
        # --- Mock Setup ---
        mock_parse_args.return_value = argparse.Namespace(
            repo="owner/repo",
            config_path=None,
            all_collaborators=True,
            user=None,
            get_user=None,
            exclude_user=None,
            json=True,
            analyze=False,
            output_csv=None
        )
        
        mock_github_api.get_collaborators.return_value = ["user1", "user2"]
        mock_reporter.gather_stats.return_value = {"user1": {"commits": 1}}

        # --- Run main ---
        main()

        # --- Assertions ---
        mock_github_api.init_github_api.assert_called_once()
        mock_github_api.get_collaborators.assert_called_with("owner", "repo")
        mock_reporter.gather_stats.assert_called_with("owner/repo", ["user1", "user2"])
        
        # Check that JSON file was opened and written to
        mock_file.assert_called_once()
        filename = mock_file.call_args[0][0]
        self.assertTrue(filename.startswith('githubReport-'))
        mock_json_dump.assert_called_once()


    @patch('argparse.ArgumentParser.parse_args')
    @patch('main.get_config')
    @patch('main.github_api')
    @patch('main.reporter')
    def test_main_specific_users_and_exclude(self, mock_reporter, mock_github_api, mock_get_config, mock_parse_args):
        """Test the main function with --user and --exclude-user flags."""
        mock_parse_args.return_value = argparse.Namespace(
            repo="owner/repo",
            config_path=None,
            all_collaborators=False,
            user=["user1", "user2", "user3"],
            get_user=None,
            exclude_user=["user2"],
            json=False,
            analyze=False,
            output_csv=None
        )
        
        # --- Run main ---
        main()

        # --- Assertions ---
        # Note: user.strip() is called inside main
        expected_users = ["user1", "user3"]
        mock_reporter.gather_stats.assert_called_with("owner/repo", expected_users)


    @patch('argparse.ArgumentParser.parse_args')
    @patch('main.get_config')
    @patch('main.github_api')
    @patch('main.reporter')
    @patch('main.analyzer')
    @patch('pandas.DataFrame.to_csv')
    def test_main_analyze_and_csv_output(self, mock_to_csv, mock_analyzer, mock_reporter, mock_github_api, mock_get_config, mock_parse_args):
        """Test the main function with --analyze and --output-csv flags."""
        mock_parse_args.return_value = argparse.Namespace(
            repo="owner/repo",
            config_path=None,
            all_collaborators=True,
            user=None,
            get_user=None,
            exclude_user=None,
            json=True, # --analyze requires --json
            analyze=True,
            output_csv="report.csv"
        )
        
        mock_github_api.get_collaborators.return_value = ["user1"]
        mock_reporter.gather_stats.return_value = {"user1": {"commits": 1}}
        
        # Mock the DataFrame returned by the analyzer
        mock_df = pd.DataFrame({'Usuário': ['user1'], 'Score': [10]})
        mock_analyzer.analyze_report.return_value = mock_df

        # --- Run main ---
        main()

        # --- Assertions ---
        mock_analyzer.analyze_report.assert_called_once()
        mock_to_csv.assert_called_with("report.csv", index=False)


if __name__ == '__main__':
    unittest.main()
