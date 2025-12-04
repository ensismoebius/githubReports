"""
GitHub Reports - Main Module

This is the main entry point for the GitHub Reports application. It orchestrates
the workflow of collecting GitHub metrics, generating reports, and performing analysis.

The application provides flexibility in:
  - Selecting which users to analyze (specific users, all collaborators)
  - Filtering users (exclusion list)
  - Output formats (console, JSON)
  - Analysis and CSV export options

Usage:
    python main.py --repo owner/repo --all-collaborators --json --analyze

Functions:
    setup_logging: Configure logging for the application
    create_argument_parser: Create CLI argument parser
    determine_usernames: Process and validate username selection
    save_json_report: Save report data to JSON file
    display_console_report: Display report data on console
    main: Main function orchestrating the application workflow
"""

# Standard library imports
import sys # Provides access to system-specific parameters and functions, used here for stderr.
import argparse # Parser for command-line options, arguments and sub-commands.
import json # Encoder and decoder for JSON data, used for saving reports.
import logging # Python's standard logging library.
from datetime import datetime # Supplies classes for manipulating dates and times, used for timestamping filenames.

# Third-party library imports
# Note: pandas is imported lazily by modules that need it (for example
# `analyzer.py`). Avoid importing it at module import time so the CLI
# can run even when pandas isn't installed (useful for lightweight runs
# and unit tests that don't require pandas).

# Local application imports
import github_api # Module for interacting with the GitHub API.
import reporter # Module responsible for gathering GitHub metrics.
import analyzer # Module for analyzing the gathered reports.
from config import get_config # Function to load configuration settings.

# Configure logging
def setup_logging():
    """Configure logging to file and stderr."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler(sys.stderr)
        ]
    )
    return logging.getLogger(__name__)

def create_argument_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(description="Recupera métricas GitHub por usuário para um repositório.")
    
    # Required arguments
    parser.add_argument("--repo", required=True, help="Repositório no formato owner/repo")
    parser.add_argument("--config-path", help="Caminho para o arquivo de configuração config.ini")
    
    # User selection (mutually exclusive)
    user_group = parser.add_mutually_exclusive_group()
    user_group.add_argument("--user", action="append", help="Nome de usuário GitHub (pode repetir várias vezes)")
    user_group.add_argument("--get-user", help="Gera o relatório para um único usuário específico.")
    user_group.add_argument("--all-collaborators", action="store_true", help="Recuperar dados para todos os colaboradores do repositório")

    # Optional arguments
    parser.add_argument("--exclude-user", action="append", help="Exclui um usuário do relatório (pode repetir várias vezes)")
    parser.add_argument("--json", action="store_true", help="Salva a saída em um arquivo JSON.")
    parser.add_argument("--analyze", action="store_true", help="Analisa o relatório JSON gerado.")
    parser.add_argument("--output-csv", help="Caminho para salvar o relatório de análise em CSV.")
    parser.add_argument("--generate-report", action="store_true", help="After CSV generation, produce a Markdown report using templates.")
    parser.add_argument("--report-template-path", help="Path to a custom Jinja2 template file to render the report.")
    parser.add_argument("--package-template-name", default="report.md.j2", help="Name of the packaged template to use (when preferring packaged templates).")
    parser.add_argument("--prefer-package-template", action="store_true", help="Prefer packaged template over a filesystem template when both provided.")
    parser.add_argument("--report-output", help="Path where the generated Markdown report should be saved.")
    
    return parser

def determine_usernames(args, logger):
    """
    Determine which usernames to process based on command-line arguments.
    
    Args:
        args: Parsed command-line arguments.
        logger: Logger instance.
        
    Returns:
        list: List of GitHub usernames to process.
        
    Raises:
        SystemExit: If no users can be determined or list becomes empty after filtering.
    """
    owner, repo = args.repo.split("/", 1)
    usernames = []
    
    if args.all_collaborators:
        usernames = github_api.get_collaborators(owner, repo)
        if not usernames:
            logger.warning(f"No collaborators found for {args.repo} or an error occurred. Exiting.")
            sys.exit(1)
    elif args.user:
        usernames = args.user
    elif args.get_user:
        usernames = [args.get_user]
    else:
        # Default: fetch all collaborators
        usernames = github_api.get_collaborators(owner, repo)
        if not usernames:
            logger.warning(f"No users specified and no collaborators found for {args.repo}. Exiting.")
            sys.exit(1)
    
    # Apply exclusions
    if args.exclude_user:
        usernames = [u for u in usernames if u not in args.exclude_user]
    
    # Clean up whitespace
    usernames = [u.strip() for u in usernames]
    
    # Verify non-empty
    if not usernames:
        logger.warning("A lista de usuários para processar está vazia. Saindo.")
        sys.exit(1)
    
    return usernames

def save_json_report(report_data, logger):
    """
    Save report data to a JSON file with timestamp.
    
    Args:
        report_data (dict): Report data to save.
        logger: Logger instance.
        
    Returns:
        str: Filename of the saved report.
    """
    now = datetime.now()
    filename = f"githubReport-{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Relatório salvo em {filename}")
    return filename

def display_console_report(report_data):
    """Display report data in human-readable format on console."""
    for username, stats in report_data.items():
        print(f"== {username} ==")
        for key, value in stats.items():
            print(f"{key}: {value}")
        print()

def main():
    """
    Main function to parse arguments, retrieve GitHub metrics,
    and generate reports or analysis.
    """
    logger = setup_logging()
    
    try:
        # Parse command-line arguments
        parser = create_argument_parser()
        args = parser.parse_args()

        # Initialize configuration and GitHub API
        config = get_config(args.config_path)
        github_api.init_github_api(config)

        # Determine which users to process
        usernames = determine_usernames(args, logger)

        # Gather statistics for the selected repository and users
        report_data = reporter.gather_stats(args.repo, usernames)
        
        # Handle output based on arguments
        if args.json:
            save_json_report(report_data, logger)
            
            # Perform analysis if requested
            if args.analyze:
                df = analyzer.analyze_report(report_data, config)
                print("\nAnálise do Relatório:")
                print(df.to_string(index=False))

                if args.output_csv:
                    df.to_csv(args.output_csv, index=False)
                    logger.info(f"Análise salva em {args.output_csv}")

                    # Optionally generate a Markdown report from the CSV
                    if getattr(args, 'generate_report', False):
                        try:
                            from markdown_report import generate_report

                            report_out = getattr(args, 'report_output', None) or args.output_csv.rsplit('.', 1)[0] + '.md'
                            generate_report(
                                args.output_csv,
                                report_out,
                                project_name=args.repo,
                                team_name=config.get('Default', 'team_name', fallback='Development Team') if hasattr(config, 'get') else 'Development Team',
                                template_path=getattr(args, 'report_template_path', None),
                                prefer_package_template=getattr(args, 'prefer_package_template', True),
                                package_template_name=getattr(args, 'package_template_name', 'report.md.j2'),
                            )
                            logger.info(f"Markdown report generated at {report_out}")
                        except Exception as e:
                            logger.error(f"Failed to generate Markdown report: {e}")
        else:
            # Display report on console
            display_console_report(report_data)
        
        logger.info("Script execution finished successfully.")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)

# Entry point for the script execution.
if __name__ == "__main__":
    main()