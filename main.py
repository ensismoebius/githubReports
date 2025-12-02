import sys
import argparse
import json
from datetime import datetime
import github_api
import reporter
import analyzer
import pandas as pd
from config import get_config

def main():
    parser = argparse.ArgumentParser(description="Recupera métricas GitHub por usuário para um repositório.")
    parser.add_argument("--repo", required=True, help="Repositório no formato owner/repo")
    parser.add_argument("--config-path", help="Caminho para o arquivo de configuração config.ini")
    
    user_group = parser.add_mutually_exclusive_group()
    user_group.add_argument("--user", action="append", help="Nome de usuário GitHub (pode repetir várias vezes)")
    user_group.add_argument("--get-user", help="Gera o relatório para um único usuário específico.")
    user_group.add_argument("--all-collaborators", action="store_true", help="Recuperar dados para todos os colaboradores do repositório")

    parser.add_argument("--exclude-user", action="append", help="Exclui um usuário do relatório (pode repetir várias vezes)")
    parser.add_argument("--json", action="store_true", help="Salva a saída em um arquivo JSON.")
    parser.add_argument("--analyze", action="store_true", help="Analisa o relatório JSON gerado.")
    parser.add_argument("--output-csv", help="Caminho para salvar o relatório de análise em CSV.")
    args = parser.parse_args()

    # Initialize configuration
    config = get_config(args.config_path)
    github_api.init_github_api(config)

    usernames_to_process = []
    if args.all_collaborators:
        owner, repo = args.repo.split("/", 1)
        usernames_to_process = github_api.get_collaborators(owner, repo)
        if not usernames_to_process:
            print(f"[WARN] No collaborators found for {args.repo} or an error occurred. Exiting.", file=sys.stderr)
            sys.exit(1)
    elif args.user:
        usernames_to_process = args.user
    elif args.get_user:
        usernames_to_process = [args.get_user]
    else:
        owner, repo = args.repo.split("/", 1)
        usernames_to_process = github_api.get_collaborators(owner, repo)
        if not usernames_to_process:
            print(f"[WARN] No users specified and no collaborators found for {args.repo}. Exiting.", file=sys.stderr)
            sys.exit(1)

    if args.exclude_user:
        usernames_to_process = [u for u in usernames_to_process if u not in args.exclude_user]

    if not usernames_to_process:
        print("[WARN] A lista de usuários para processar está vazia. Saindo.", file=sys.stderr)
        sys.exit(1)

    out = reporter.gather_stats(args.repo, usernames_to_process)
    
    if args.json:
        now = datetime.now()
        filename = f"githubReport-{now.strftime('%Y-%m-%d_%H-%M-%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"Relatório salvo em {filename}", file=sys.stderr)
        
        if args.analyze:
            df = analyzer.analyze_report(out, config)
            print("\nAnálise do Relatório:")
            print(df.to_string(index=False))
            
            if args.output_csv:
                df.to_csv(args.output_csv, index=False)
                print(f"\nAnálise salva em {args.output_csv}", file=sys.stderr)
    else:
        for u, s in out.items():
            print(f"== {u} ==")
            for k, v in s.items():
                print(f"{k}: {v}")
            print()

if __name__ == "__main__":
    main()