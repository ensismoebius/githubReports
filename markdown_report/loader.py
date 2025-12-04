"""Data loading utilities for Markdown report generator.

This loader is resilient to CSVs produced by the analyzer which use
Portuguese, human-friendly column headers (for example: "Usuário",
"Commits", "PRs Abertos"). It normalizes column names into the
English, snake_case names the report generator expects (for example:
`username`, `commits`, `prs_opened`).
"""
from __future__ import annotations

import logging
import unicodedata
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


_PORTUGUESE_TO_ENGLISH: Dict[str, str] = {
    'usuário': 'username',
    'usuario': 'username',
    'score': 'total_points',
    'conceito': 'grade',
    'commits': 'commits',
    'bônus commits': 'bonus_mb',
    'bonus commits': 'bonus_mb',
    'imagens': 'images',
    'issues criadas': 'issues_created',
    'issues criadas': 'issues_created',
    'issues resolvidas': 'issues_resolved',
    'prs abertos': 'prs_opened',
    'prs aprovados': 'prs_approved',
    'comentários': 'comments',
    'comentarios': 'comments',
}


def _strip_accents(s: str) -> str:
    """Return a lower-cased string without diacritics.

    Examples: 'Usuário' -> 'usuario', 'Bônus Commits' -> 'bonus commits'
    """
    if not isinstance(s, str):
        return s
    nkfd = unicodedata.normalize('NFKD', s)
    stripped = ''.join(ch for ch in nkfd if not unicodedata.combining(ch))
    return stripped.lower()


def _map_column(name: str) -> str:
    """Map a human-friendly column name to the canonical internal name.

    Falls back to a normalized snake_case of the header when no direct
    mapping is known.
    """
    norm = _strip_accents(name).strip()
    if norm in _PORTUGUESE_TO_ENGLISH:
        return _PORTUGUESE_TO_ENGLISH[norm]
    # Fallback: replace non-alphanum with underscore and collapse underscores
    import re

    fallback = re.sub(r'[^a-z0-9]+', '_', norm).strip('_')
    return fallback


def load_data(csv_file_path: str) -> pd.DataFrame:
    """Load and normalize GitHub CSV data for the report generator.

    The function reads the CSV with pandas and then normalizes column
    names so the rest of the report code can rely on a consistent set
    of English, snake_case keys.
    """
    try:
        df = pd.read_csv(csv_file_path)
        # Normalize column names
        new_cols = {}
        for col in df.columns:
            new_cols[col] = _map_column(col)
        df = df.rename(columns=new_cols)
        # Provide sensible defaults for commonly referenced numeric columns
        for col in (
            'lines_added', 'lines_deleted', 'prs_opened', 'prs_approved',
            'issues_created', 'issues_resolved', 'commits', 'comments', 'images',
            'total_points'
        ):
            if col not in df.columns:
                df[col] = 0
        logger.info(f"Loaded data from {csv_file_path}")
        return df
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        raise
