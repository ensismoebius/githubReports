# Standard library imports
import sys # Provides access to system-specific parameters and functions, used here for stderr.
import argparse # Parser for command-line options, arguments and sub-commands.
import json # Encoder and decoder for JSON data, used for saving reports.
from datetime import datetime # Supplies classes for manipulating dates and times, used for timestamping filenames.

# Third-party library imports
import pandas as pd # Data analysis and manipulation tool, used for report analysis.

# Local application imports
import github_api # Module for interacting with the GitHub API.
import reporter # Module responsible for gathering GitHub metrics.
import analyzer # Module for analyzing the gathered reports.
from config import get_config # Function to load configuration settings.

def main():
    """
    Main function to parse arguments, retrieve GitHub metrics,
    and generate reports or analysis.
    """
    # Initialize the argument parser with a description of the script's purpose.
    parser = argparse.ArgumentParser(description="Recupera métricas GitHub por usuário para um repositório.")
    
    # Define command-line arguments.
    parser.add_argument("--repo", required=True, help="Repositório no formato owner/repo")
    parser.add_argument("--config-path", help="Caminho para o arquivo de configuração config.ini")
    
    # Create a mutually exclusive group for user selection to ensure only one method is used.
    user_group = parser.add_mutually_exclusive_group()
    user_group.add_argument("--user", action="append", help="Nome de usuário GitHub (pode repetir várias vezes)")
    user_group.add_argument("--get-user", help="Gera o relatório para um único usuário específico.")
    user_group.add_argument("--all-collaborators", action="store_true", help="Recuperar dados para todos os colaboradores do repositório")

    parser.add_argument("--exclude-user", action="append", help="Exclui um usuário do relatório (pode repetir várias vezes)")
    parser.add_argument("--json", action="store_true", help="Salva a saída em um arquivo JSON.")
    parser.add_argument("--analyze", action="store_true", help="Analisa o relatório JSON gerado.")
    parser.add_argument("--output-csv", help="Caminho para salvar o relatório de análise em CSV.")
    
    # Parse the arguments provided by the user.
    args = parser.parse_args()

    # Initialize configuration using the provided path or default.
    # This loads settings like GitHub API tokens.
    config = get_config(args.config_path)
    # Initialize the GitHub API module with the loaded configuration.
    github_api.init_github_api(config)

    usernames_to_process = []
    # Determine which users to process based on command-line arguments.
    if args.all_collaborators:
        # If --all-collaborators is specified, fetch all collaborators for the given repository.
        owner, repo = args.repo.split("/", 1)
        usernames_to_process = github_api.get_collaborators(owner, repo)
        if not usernames_to_process:
            # If no collaborators are found, print a warning and exit.
            print(f"[WARN] No collaborators found for {args.repo} or an error occurred. Exiting.", file=sys.stderr)
            sys.exit(1)
    elif args.user:
        # If --user is specified, use the provided usernames.
        usernames_to_process = args.user
    elif args.get_user:
        # If --get-user is specified, process only that single user.
        usernames_to_process = [args.get_user]
    else:
        # If no specific user argument, default to fetching all collaborators.
        owner, repo = args.repo.split("/", 1)
        usernames_to_process = github_api.get_collaborators(owner, repo)
        if not usernames_to_process:
            # If no users are specified and no collaborators found, print a warning and exit.
            print(f"[WARN] No users specified and no collaborators found for {args.repo}. Exiting.", file=sys.stderr)
            sys.exit(1)

    # Exclude specified users from the list if --exclude-user was used.
    if args.exclude_user:
        usernames_to_process = [u for u in usernames_to_process if u not in args.exclude_user]

    # Check if there are any users left to process after all filtering.
    if not usernames_to_process:
        print("[WARN] A lista de usuários para processar está vazia. Saindo.", file=sys.stderr)
        sys.exit(1)

    # Gather statistics for the selected repository and users.
    out = reporter.gather_stats(args.repo, usernames_to_process)
    
    # Handle output based on the --json argument.
    if args.json:
        # Generate a timestamped filename for the JSON report.
        now = datetime.now()
        filename = f"githubReport-{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        # Write the gathered statistics to a JSON file.
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"Relatório salvo em {filename}", file=sys.stderr)
        
        # If --analyze is also specified, perform analysis.
        if args.analyze:
            # Analyze the report data using the analyzer module.
            df = analyzer.analyze_report(out, config)
            print("\nAnálise do Relatório:")
            # Print the analysis result to the console.
            print(df.to_string(index=False))
            
            # If --output-csv is specified, save the analysis to a CSV file.
            if args.output_csv:
                df.to_csv(args.output_csv, index=False)
                print(f"\nAnálise salva em {args.output_csv}", file=sys.stderr)
    else:
        # If not saving as JSON, print the report to the console in a human-readable format.
        for u, s in out.items():
            print(f"== {u} ==")
            for k, v in s.items():
                print(f"{k}: {v}")
            print()

# Entry point for the script execution.
if __name__ == "__main__":
    main()