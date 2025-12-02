import configparser # Module for reading and writing configuration files.
import os # Provides a way of using operating system dependent functionality, used for file path checks.
import sys # Provides access to system-specific parameters and functions, though not directly used for output here, often useful for error messages.

def get_config(config_path=None):
    """
    Loads configuration from a specified file. If the file does not exist,
    it interactively prompts the user for necessary information (like GitHub token)
    and creates a new configuration file with default scoring and grading settings.

    Args:
        config_path (str, optional): The path to the configuration file.
                                     Defaults to 'config.ini' if None.

    Returns:
        configparser.ConfigParser: A ConfigParser object containing the loaded
                                   or newly created configuration.
    """
    # Set default config file path if not provided.
    if config_path is None:
        config_path = 'config.ini'

    # Initialize the ConfigParser object.
    config = configparser.ConfigParser()
    
    # Check if the configuration file exists.
    if not os.path.exists(config_path):
        # If the file does not exist, prompt the user to create it.
        print(f"Config file '{config_path}' not found. Please provide the following information:")
        
        # Prompt for GitHub token, essential for API access.
        github_token = input("Enter your GitHub token: ")
        # Prompt for GitHub API URL, with a default value.
        github_api_url = input("Enter GitHub API URL (or press Enter for default 'https://api.github.com'): ")
        if not github_api_url:
            github_api_url = "https://api.github.com"
        
        # Prompt for an optional default repository.
        repo = input("Enter default repository (owner/repo) or press Enter to skip: ")

        # Define the 'GitHub' section with API token and URL.
        config['GitHub'] = {
            'Token': github_token,
            'ApiUrl': github_api_url,
        }
        # If a default repository was provided, add it to a 'Default' section.
        if repo:
            config['Default'] = {'Repository': repo}
        
        # Define the 'Scoring' section with default point values for various GitHub activities.
        config['Scoring'] = {
            'PointsPerCommit': '2',
            'BonusMbCommitsThreshold': '19', # Threshold for bonus points based on commits.
            'BonusMbPoints': '20',           # Bonus points for reaching the commit threshold.
            'PointsPerImage': '4',
            'PointsPerIssueCreated': '1',
            'PointsPerIssueResolved': '3',
            'PointsPerPrOpened': '2',
            'PointsPerPrApproved': '3',
            'PointsPerComment': '1'
        }
        
        # Define the 'Grades' section with thresholds for different performance grades.
        config['Grades'] = {
            'MB': '70', # "Muito Bom" (Very Good) threshold
            'B': '40',  # "Bom" (Good) threshold
            'R': '15'   # "Regular" (Regular) threshold
        }
        
        # Define the 'Extensions' section for file types, e.g., image extensions for counting.
        config['Extensions'] = {
            'Image': '.jpg, .jpeg, .png, .gif, .svg, .bmp, .webp'
        }

        # Write the newly created configuration to the specified file.
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        
        print(f"Configuration saved to '{config_path}'.")
        
    # Read the configuration from the file (either existing or newly created).
    config.read(config_path)
    return config

# This block allows the script to be run directly to test config loading and display.
if __name__ == '__main__':
    # Load the configuration.
    config = get_config()
    print("Configuration loaded.")
    # Print out all sections and their key-value pairs for verification.
    for section in config.sections():
        print(f"[{section}]")
        for key in config[section]:
            print(f"  {key} = {config[section][key]}")