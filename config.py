import configparser
import os
import sys

def get_config(config_path=None):
    if config_path is None:
        config_path = 'config.ini'

    config = configparser.ConfigParser()
    
    if not os.path.exists(config_path):
        print(f"Config file '{config_path}' not found. Please provide the following information:")
        
        github_token = input("Enter your GitHub token: ")
        github_api_url = input("Enter GitHub API URL (or press Enter for default 'https://api.github.com'): ")
        if not github_api_url:
            github_api_url = "https://api.github.com"
        
        repo = input("Enter default repository (owner/repo) or press Enter to skip: ")

        config['GitHub'] = {
            'Token': github_token,
            'ApiUrl': github_api_url,
        }
        if repo:
            config['Default'] = {'Repository': repo}
        
        config['Scoring'] = {
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
        
        config['Grades'] = {
            'MB': '70',
            'B': '40',
            'R': '15'
        }
        
        config['Extensions'] = {
            'Image': '.jpg, .jpeg, .png, .gif, .svg, .bmp, .webp'
        }

        with open(config_path, 'w') as configfile:
            config.write(configfile)
        
        print(f"Configuration saved to '{config_path}'.")
        
    config.read(config_path)
    return config

if __name__ == '__main__':
    config = get_config()
    print("Configuration loaded.")
    for section in config.sections():
        print(f"[{section}]")
        for key in config[section]:
            print(f"  {key} = {config[section][key]}")