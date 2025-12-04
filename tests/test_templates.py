import pytest
import tempfile
import os
from markdown_report import generate_report
import pandas as pd


@pytest.fixture
def minimal_df():
    return pd.DataFrame({
        'username': ['user1', 'user2'],
        'commits': [10, 5],
        'images': [0, 0],
        'lines_added': [1000, 500],
        'lines_deleted': [100, 50],
        'issues_created': [2, 1],
        'issues_resolved': [1, 0],
        'prs_opened': [3, 1],
        'prs_approved': [2, 1],
        'comments': [5, 2],
        'total_points': [100, 50],
        'grade': ['MB', 'B'],
    })


def test_generate_with_packaged_template(minimal_df):
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, 'data.csv')
        out_path = os.path.join(tmpdir, 'report.md')
        # prepare csv
        import pandas as pd
        minimal_df.to_csv(csv_path, index=False)

        # Should succeed using packaged template
        report = generate_report(csv_path, out_path, project_name='T', team_name='Team', template_only=True)
        assert os.path.exists(out_path)
        with open(out_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert '## 📊 Executive Summary' in content


def test_template_only_missing_raises(minimal_df):
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, 'data.csv')
        out_path = os.path.join(tmpdir, 'report.md')
        minimal_df.to_csv(csv_path, index=False)

        # Non-existent template path should raise when template_only=True
        with pytest.raises(Exception):
            generate_report(csv_path, out_path, template_path='/no/such/template.md.j2', template_only=True)
