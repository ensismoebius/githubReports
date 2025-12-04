"""
Configuration Module

This module handles loading and creating application configuration files.
It manages GitHub API settings, scoring rules, grade thresholds, and file extensions.

When a config file doesn't exist, the module prompts the user for essential
information (GitHub token) and creates a new configuration with sensible defaults.

Configuration Sections:
    GitHub: API URL and authentication token
    Default: Optional default repository
    Scoring: Point values for various GitHub metrics
    Grades: Performance grade thresholds
    Extensions: File type extensions (e.g., image files)

Functions:
    get_config: Load or create configuration
    _create_new_config: Interactively create new configuration
    _save_config: Write configuration to file
    _prompt_for_github_config: Prompt for GitHub settings
    _prompt_for_optional_config: Prompt for optional settings
"""

import configparser  # Module for reading and writing configuration files.
import os            # Provides a way of using operating system dependent functionality, used for file path checks.
import sys           # Provides access to system-specific parameters and functions.

# ============================================================================
# Default Configuration Values
# ============================================================================

DEFAULT_CONFIG_PATH = 'config.ini'
DEFAULT_GITHUB_API_URL = 'https://api.github.com'

DEFAULT_GITHUB_CONFIG = {
    'Token': '',
    'ApiUrl': DEFAULT_GITHUB_API_URL,
}

DEFAULT_SCORING_CONFIG = {
    'PointsPerCommit': '2',
    'BonusMbCommitsThreshold': '19',
    'BonusMbPoints': '20',
    'PointsPerImage': '4',
    'PointsPerIssueCreated': '1',
    'PointsPerIssueResolved': '3',
    'PointsPerPrOpened': '2',
    'PointsPerPrApproved': '3',
    'PointsPerComment': '1'
}

DEFAULT_GRADES_CONFIG = {
    'MB': '70',  # "Muito Bom" (Very Good)
    'B': '40',   # "Bom" (Good)
    'R': '15'    # "Regular" (Regular)
}

DEFAULT_EXTENSIONS_CONFIG = {
    'Image': '.jpg, .jpeg, .png, .gif, .svg, .bmp, .webp'
}

# ============================================================================
# Configuration Functions
# ============================================================================

def _prompt_for_github_config():
    """
    Interactively prompt the user for GitHub API configuration.
    
    Returns:
        dict: Configuration dictionary for GitHub settings.
    """
    github_token = input("Enter your GitHub token: ")
    github_api_url = input("Enter GitHub API URL (or press Enter for default): ").strip()
    
    if not github_api_url:
        github_api_url = DEFAULT_GITHUB_API_URL
    
    return {
        'Token': github_token,
        'ApiUrl': github_api_url,
    }

def _prompt_for_optional_config():
    """
    Interactively prompt the user for optional configuration.
    
    Returns:
        dict: Optional configuration (e.g., default repository).
    """
    repo = input("Enter default repository (owner/repo) or press Enter to skip: ").strip()
    
    if repo:
        return {'Repository': repo}
    return {}

def _create_new_config():
    """
    Create a new configuration object with user input.
    
    Returns:
        configparser.ConfigParser: A new configuration object.
    """
    print("Config file not found. Please provide the following information:")
    
    config = configparser.ConfigParser()
    
    # GitHub configuration
    config['GitHub'] = _prompt_for_github_config()
    
    # Optional configuration
    optional = _prompt_for_optional_config()
    if optional:
        config['Default'] = optional
    
    # Scoring configuration
    config['Scoring'] = DEFAULT_SCORING_CONFIG.copy()
    
    # Grades configuration
    config['Grades'] = DEFAULT_GRADES_CONFIG.copy()
    
    # Extensions configuration
    config['Extensions'] = DEFAULT_EXTENSIONS_CONFIG.copy()
    
    return config

def _save_config(config, config_path):
    """
    Save configuration to file.
    
    Args:
        config (configparser.ConfigParser): Configuration to save.
        config_path (str): Path where to save the configuration.
    """
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    print(f"Configuration saved to '{config_path}'.")

def get_config(config_path=None):
    """
    Load configuration from a specified file. If the file does not exist,
    it interactively prompts the user for necessary information and creates
    a new configuration file with default settings.

    Args:
        config_path (str, optional): The path to the configuration file.
                                     Defaults to 'config.ini' if None.

    Returns:
        configparser.ConfigParser: A ConfigParser object containing the loaded
                                   or newly created configuration.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH

    config = configparser.ConfigParser()
    
    if not os.path.exists(config_path):
        config = _create_new_config()
        _save_config(config, config_path)
    else:
        config.read(config_path)
    
    return config

# ============================================================================
# Entry Point for Testing
# ============================================================================

if __name__ == '__main__':
    config = get_config()
    print("Configuration loaded.")
    for section in config.sections():
        print(f"[{section}]")
        for key in config[section]:
            print(f"  {key} = {config[section][key]}")