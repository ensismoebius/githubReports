"""Data loading utilities for Markdown report generator."""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def load_data(csv_file_path: str) -> pd.DataFrame:
    """Load and validate GitHub data from CSV file.

    Returns a DataFrame. Raises FileNotFoundError on missing file and
    propagates other exceptions from pandas.
    """
    try:
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded data from {csv_file_path}")
        return df
    except FileNotFoundError:
        logger.error(f"CSV file not found: {csv_file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        raise
