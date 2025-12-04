import csv
import tempfile
from pathlib import Path

import pytest

from markdown_report import generate_report


def test_generate_report_from_portuguese_csv():
    # Create a temporary directory for test files
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create a CSV that mimics the analyzer output (Portuguese headers)
        csv_path = tmp_path / "portuguese.csv"
        rows = [
            [
                'Usuário', 'Score', 'Conceito', 'Commits', 'Bônus Commits',
                'Imagens', 'Issues Criadas', 'Issues Resolvidas', 'PRs Abertos',
                'PRs Aprovados', 'Comentários'
            ],
            ['jujuli2', '50', 'B', '7', '0', '0', '9', '0', '7', '0', '1']
        ]

        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        out_md = tmp_path / "out.md"

        # Should not raise KeyError and should produce a markdown string
        report = generate_report(str(csv_path), str(out_md), project_name="test/project", team_name="Team")
        assert isinstance(report, str)
        assert out_md.exists()
