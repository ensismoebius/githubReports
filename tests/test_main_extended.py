"""
Extended tests for main module covering helper functions and error cases.
Tests for: setup_logging, create_argument_parser, determine_usernames
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
import argparse
import logging

from main import (
    setup_logging,
    create_argument_parser,
    determine_usernames
)


class TestMainExtended(unittest.TestCase):

    def test_setup_logging_creates_logger(self):
        """Test that setup_logging returns a logger."""
        logger = setup_logging()
        self.assertIsInstance(logger, logging.Logger)
        # Logger name will be 'main' when imported as module
        self.assertIn(logger.name, ['__main__', 'main'])

    def test_setup_logging_has_handlers(self):
        """Test that setup_logging configures handlers."""
        logger = logging.getLogger()
        # Clear existing handlers
        logger.handlers = []
        
        setup_logging()
        # Should have at least 2 handlers (file + stderr)
        self.assertGreaterEqual(len(logger.handlers), 2)

    def test_create_argument_parser_has_required_args(self):
        """Test that parser includes required arguments."""
        parser = create_argument_parser()
        
        # Should be able to parse with required args
        args = parser.parse_args(['--repo', 'owner/repo'])
        self.assertEqual(args.repo, 'owner/repo')

    def test_create_argument_parser_mutually_exclusive_users(self):
        """Test that user selection arguments are mutually exclusive."""
        parser = create_argument_parser()
        
        with self.assertRaises(SystemExit):
            parser.parse_args(['--repo', 'owner/repo', '--user', 'user1', '--all-collaborators'])

    def test_create_argument_parser_optional_args(self):
        """Test parser handles optional arguments."""
        parser = create_argument_parser()
        
        args = parser.parse_args([
            '--repo', 'owner/repo',
            '--user', 'user1',
            '--exclude-user', 'user2',
            '--json',
            '--analyze',
            '--output-csv', 'report.csv'
        ])
        
        self.assertEqual(args.repo, 'owner/repo')
        self.assertIn('user1', args.user)
        self.assertIn('user2', args.exclude_user)
        self.assertTrue(args.json)
        self.assertTrue(args.analyze)
        self.assertEqual(args.output_csv, 'report.csv')

    def test_create_argument_parser_multiple_users(self):
        """Test parser handles multiple --user arguments."""
        parser = create_argument_parser()
        
        args = parser.parse_args([
            '--repo', 'owner/repo',
            '--user', 'user1',
            '--user', 'user2',
            '--user', 'user3'
        ])
        
        self.assertEqual(args.user, ['user1', 'user2', 'user3'])

    def test_create_argument_parser_multiple_exclude_users(self):
        """Test parser handles multiple --exclude-user arguments."""
        parser = create_argument_parser()
        
        args = parser.parse_args([
            '--repo', 'owner/repo',
            '--all-collaborators',
            '--exclude-user', 'user1',
            '--exclude-user', 'user2'
        ])
        
        self.assertEqual(args.exclude_user, ['user1', 'user2'])

    @patch('main.github_api')
    def test_determine_usernames_all_collaborators(self, mock_github_api):
        """Test determine_usernames with --all-collaborators flag."""
        mock_github_api.get_collaborators.return_value = ['user1', 'user2', 'user3']
        
        args = argparse.Namespace(
            repo='owner/repo',
            all_collaborators=True,
            user=None,
            get_user=None,
            exclude_user=None
        )
        logger = logging.getLogger(__name__)
        
        usernames = determine_usernames(args, logger)
        self.assertEqual(usernames, ['user1', 'user2', 'user3'])

    @patch('main.github_api')
    def test_determine_usernames_specific_users(self, mock_github_api):
        """Test determine_usernames with specific --user arguments."""
        args = argparse.Namespace(
            repo='owner/repo',
            all_collaborators=False,
            user=['user1', 'user2'],
            get_user=None,
            exclude_user=None
        )
        logger = logging.getLogger(__name__)
        
        usernames = determine_usernames(args, logger)
        self.assertEqual(usernames, ['user1', 'user2'])

    @patch('main.github_api')
    def test_determine_usernames_with_get_user(self, mock_github_api):
        """Test determine_usernames with --get-user argument."""
        args = argparse.Namespace(
            repo='owner/repo',
            all_collaborators=False,
            user=None,
            get_user='single_user',
            exclude_user=None
        )
        logger = logging.getLogger(__name__)
        
        usernames = determine_usernames(args, logger)
        self.assertEqual(usernames, ['single_user'])

    @patch('main.github_api')
    def test_determine_usernames_exclude_users(self, mock_github_api):
        """Test determine_usernames excludes specified users."""
        args = argparse.Namespace(
            repo='owner/repo',
            all_collaborators=False,
            user=['user1', 'user2', 'user3'],
            get_user=None,
            exclude_user=['user2']
        )
        logger = logging.getLogger(__name__)
        
        usernames = determine_usernames(args, logger)
        self.assertEqual(usernames, ['user1', 'user3'])

    @patch('main.github_api')
    def test_determine_usernames_exclude_multiple_users(self, mock_github_api):
        """Test determine_usernames excludes multiple specified users."""
        args = argparse.Namespace(
            repo='owner/repo',
            all_collaborators=False,
            user=['user1', 'user2', 'user3', 'user4'],
            get_user=None,
            exclude_user=['user2', 'user4']
        )
        logger = logging.getLogger(__name__)
        
        usernames = determine_usernames(args, logger)
        self.assertEqual(usernames, ['user1', 'user3'])

    @patch('main.sys.exit')
    @patch('main.github_api')
    def test_determine_usernames_no_collaborators_error(self, mock_github_api, mock_exit):
        """Test determine_usernames exits when no collaborators found."""
        mock_github_api.get_collaborators.return_value = []
        
        args = argparse.Namespace(
            repo='owner/repo',
            all_collaborators=True,
            user=None,
            get_user=None,
            exclude_user=None
        )
        logger = logging.getLogger(__name__)
        
        determine_usernames(args, logger)
        mock_exit.assert_called_with(1)

    @patch('main.sys.exit')
    @patch('main.github_api')
    def test_determine_usernames_all_excluded_error(self, mock_github_api, mock_exit):
        """Test determine_usernames exits when all users are excluded."""
        args = argparse.Namespace(
            repo='owner/repo',
            all_collaborators=False,
            user=['user1', 'user2'],
            get_user=None,
            exclude_user=['user1', 'user2']
        )
        logger = logging.getLogger(__name__)
        
        determine_usernames(args, logger)
        mock_exit.assert_called_with(1)

    @patch('main.github_api')
    def test_determine_usernames_whitespace_handling(self, mock_github_api):
        """Test determine_usernames strips whitespace from usernames."""
        args = argparse.Namespace(
            repo='owner/repo',
            all_collaborators=False,
            user=['  user1  ', 'user2'],
            get_user=None,
            exclude_user=None
        )
        logger = logging.getLogger(__name__)
        
        usernames = determine_usernames(args, logger)
        self.assertEqual(usernames, ['user1', 'user2'])

    @patch('main.sys.exit')
    @patch('main.github_api')
    def test_determine_usernames_default_collaborators(self, mock_github_api, mock_exit):
        """Test determine_usernames defaults to getting collaborators."""
        mock_github_api.get_collaborators.return_value = ['user1', 'user2']
        
        args = argparse.Namespace(
            repo='owner/repo',
            all_collaborators=False,
            user=None,
            get_user=None,
            exclude_user=None
        )
        logger = logging.getLogger(__name__)
        
        usernames = determine_usernames(args, logger)
        self.assertEqual(usernames, ['user1', 'user2'])


if __name__ == '__main__':
    unittest.main()
