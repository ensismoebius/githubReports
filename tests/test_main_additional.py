import unittest
from unittest.mock import patch, MagicMock
import argparse
import configparser
import pandas as pd

from main import main

class TestMainAdditional(unittest.TestCase):
    @patch('argparse.ArgumentParser.parse_args')
    @patch('main.get_config')
    @patch('main.github_api')
    @patch('main.reporter')
    @patch('main.analyzer')
    @patch('pandas.DataFrame.to_csv')
    @patch('markdown_report.generate_report')
    def test_generate_report_with_missing_team_name_uses_default(self, mock_generate_report, mock_to_csv, mock_analyzer, mock_reporter, mock_github_api, mock_get_config, mock_parse_args):
        # setup args
        mock_parse_args.return_value = argparse.Namespace(
            repo="owner/repo",
            config_path=None,
            all_collaborators=True,
            user=None,
            get_user=None,
            exclude_user=None,
            json=True,
            analyze=True,
            output_csv="report.csv",
            generate_report=True,
            report_template_path=None,
            prefer_package_template=True,
            package_template_name='report.md.j2',
            report_output=None
        )
        # config missing Default section
        cfg = configparser.ConfigParser()
        mock_get_config.return_value = cfg

        mock_github_api.get_collaborators.return_value = ["user1"]
        mock_reporter.gather_stats.return_value = {"user1": {"commits": 1}}
        mock_df = pd.DataFrame({'Usuário': ['user1'], 'Score': [10]})
        mock_analyzer.analyze_report.return_value = mock_df

        # run
        main()

        # generate_report should be called and used default team name
        self.assertTrue(mock_generate_report.called)
        called_args, called_kwargs = mock_generate_report.call_args
        self.assertEqual(called_kwargs.get('team_name'), 'Development Team')

if __name__ == '__main__':
    unittest.main()
