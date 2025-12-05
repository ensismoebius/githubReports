# GitHub Reports Generator

This is a Python-based tool designed to fetch data from GitHub, analyze repository activity, and generate comprehensive reports. It provides insights into contributions, issues, pull requests, and more, with configurable scoring and grading metrics.

## Features

*   **GitHub API Integration**: Seamlessly fetches data directly from the GitHub API.
*   **Activity Analysis**: Analyzes various aspects of repository activity, including commits, issues created/resolved, pull requests opened/approved, and comments.
*   **Configurable Scoring**: Calculates contribution scores based on customizable metrics (e.g., points per commit, per issue, per PR).
*   **Grading System**: Applies a configurable grading system (e.g., MB, B, R) based on calculated scores.
*   **Detailed Reports**: Generates detailed reports summarizing repository activity and contributor performance.

## Installation

To get started with the GitHub Reports Generator, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ensismoebius/githubReports
    cd githubReports
    ```

2.  **Install dependencies**:
    Ensure you have Python 3 installed. Then, install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The tool uses a `config.ini` file for its settings. If `config.ini` does not exist when you first run `main.py`, the `config.py` script will guide you through creating one by prompting for necessary information.

### Sample config.ini

Here is a sample configuration file with typical settings:

```ini
[GitHub]
token = github_pat_YOUR_TOKEN_HERE
apiurl = https://api.github.com

[Default]
team_name = Development Team

[Scoring]
PointsPerCommit = 2
BonusMbCommitsThreshold = 19
BonusMbPoints = 20
PointsPerImage = 4
PointsPerIssueCreated = 1
PointsPerIssueResolved = 3
PointsPerPrOpened = 2
PointsPerPrApproved = 3
PointsPerComment = 1

[Grades]
MB = 70
B = 40
R = 15

[Extensions]
image = .jpg, .jpeg, .png, .gif, .svg, .bmp, .webp
```

### Configuration Details

*   **GitHub Token**: A personal access token is required for authentication with the GitHub API. This is essential for fetching data, especially from private repositories or to avoid rate limits. Generate one at [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens).
*   **GitHub API URL**: The base URL for the GitHub API (defaults to `https://api.github.com`). Change only if using GitHub Enterprise Server.
*   **Team Name**: A friendly name for your team (used in reports).
*   **Scoring Parameters**: Define points for different actions:
    - `PointsPerCommit`: Points awarded per commit (default: 2).
    - `BonusMbCommitsThreshold`: Minimum commits to qualify for bonus points (default: 19).
    - `BonusMbPoints`: Bonus points awarded when threshold is reached (default: 20).
    - `PointsPerImage`: Points per image file committed (default: 4).
    - `PointsPerIssueCreated`, `PointsPerIssueResolved`: Points for issue activity.
    - `PointsPerPrOpened`, `PointsPerPrApproved`: Points for PR activity.
    - `PointsPerComment`: Points per discussion comment (default: 1).
*   **Grading Thresholds**: Set score thresholds for different grades:
    - `MB` (Elite): ≥70 points
    - `B` (Strong): ≥40 points
    - `R` (Regular): ≥15 points
    - `I` (Needs Boost): <15 points
*   **Image Extensions**: A comma-separated list of file extensions to be considered as images for scoring purposes.

## Usage

After installation and configuration, you can run the report generator using `main.py`:

```bash
python main.py
```

This will execute the analysis based on your `config.ini` settings and generate the reports. You may be prompted for additional repository information if not specified in the configuration.

## Recent Changes (quick summary)

The project received several improvements to make it more robust and easier to debug:

- **Logging changes**: The application now writes persistent logs to the system temporary directory (`/tmp/app.log` by default). Console output is quiet by default and only shows ERROR-level messages.
- **Verbose console output**: Add `--verbose` (or `-v`) to the CLI to enable INFO-level messages on the console for debugging.
- **CSV header normalization**: The Markdown report loader normalizes Portuguese human-friendly headers (for example `Usuário`, `PRs Abertos`) into the canonical English snake_case columns the renderer expects. This makes the CSV output from the analyzer directly consumable by the report generator.
- **Lazy pandas import**: The main script no longer imports `pandas` at module-import time; modules that need `pandas` import it locally. This allows running the CLI for some operations even when `pandas` isn't installed.
- **Tests and temp files**: Tests now write their temporary outputs into the system temp directory using `tempfile.TemporaryDirectory()` so test artifacts are isolated and cleaned up automatically.

## Logging and Debugging

- By default the CLI writes logs to `/tmp/app.log` and prints only errors to the console. To enable more verbose console logging for debugging, run:

```bash
python main.py --repo owner/repo --user someuser --json --verbose
```

- The file `/tmp/app.log` contains INFO-level logs and above for the full execution trace.

## CSV input compatibility

If you generate CSV reports using the included analyzer, the Markdown report generator will accept the analyzer's Portuguese column headers and map them to the internal column names automatically. No manual column renaming is required.

## Running Tests

Run the test suite with:

```bash
pytest
```

Tests create temporary files under the system temp directory and clean them up automatically; you should not need to modify tests to change where temporary files are stored.

## CLI Examples

- Run analysis and save JSON report:

```bash
python main.py --repo owner/repo --user username --json
```

- Run analysis, export CSV and generate Markdown (verbose console):

```bash
python main.py --repo owner/repo --user username --json --analyze --output-csv report.csv --generate-report --report-output report.md --verbose
```

## Developer Guide

### Running Tests

The project uses `pytest` for unit and integration testing. Run the full test suite with:

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_analyzer.py
```

To run a specific test:

```bash
pytest tests/test_analyzer.py::test_analyze_report
```

To run tests with verbose output:

```bash
pytest -v
```

To run tests with coverage report:

```bash
pytest --cov=. --cov-report=html
```

**Note**: All tests write temporary files to the system temp directory (`/tmp` on Linux/macOS, `%TEMP%` on Windows) and clean them up automatically after execution.

### Debugging Logs

The application writes detailed logs to `/tmp/app.log` (or `%TEMP%\app.log` on Windows). To inspect logs from a previous run:

```bash
# View the last 20 lines of the log
tail -20 /tmp/app.log

# Watch logs in real-time (useful when running in another terminal)
tail -f /tmp/app.log

# Search logs for errors
grep ERROR /tmp/app.log

# Clear the log before a fresh run
truncate -s 0 /tmp/app.log
```

To enable verbose console output during development, use the `--verbose` flag:

```bash
python main.py --repo owner/repo --user username --json --verbose
```

This will print INFO-level logs to stderr in addition to writing them to `/tmp/app.log`.

### Project Structure

```
githubReports/
├── main.py                      # Entry point for the CLI
├── analyzer.py                  # Report analysis and scoring logic
├── reporter.py                  # GitHub API statistics collector
├── config.py                    # Configuration file handler
├── config.ini                   # Configuration file (create via config.py)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── github_api/                  # GitHub API wrapper modules
│   ├── __init__.py
│   ├── core.py                  # API initialization
│   ├── commits.py               # Commit-related queries
│   ├── issues.py                # Issue queries
│   ├── pulls.py                 # Pull request queries
│   ├── users.py                 # User profile queries
│   ├── metrics.py               # Metrics calculations
│   └── __pycache__/
│
├── markdown_report/             # Markdown report generation
│   ├── __init__.py
│   ├── generator.py             # Report orchestration (Jinja2 + fallback)
│   ├── loader.py                # CSV data loader with header normalization
│   ├── stats.py                 # Statistics and archetype detection
│   ├── sections.py              # Report section builders (fallback mode)
│   ├── utils.py                 # Formatting and helper utilities
│   ├── templates/               # Jinja2 templates
│   │   ├── report.md.j2
│   │   └── partials/            # Template partials
│   │       ├── header.j2
│   │       ├── summary.j2
│   │       ├── leaderboard.j2
│   │       └── ...
│   └── __pycache__/
│
├── tests/                       # Unit and integration tests
│   ├── __init__.py
│   ├── test_analyzer.py
│   ├── test_main.py
│   ├── test_github_api.py
│   ├── test_markdown_report_generator.py
│   ├── test_markdown_loader_portuguese_columns.py
│   └── ...
│
└── reports/                     # Output directory for generated reports
    ├── report.md
    ├── report.csv
    └── ...
```

### Adding New Tests

Tests should use `tempfile.TemporaryDirectory()` for any file I/O:

```python
import tempfile
from pathlib import Path

def test_my_feature():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create test files in tmp_path
        test_file = tmp_path / "test.csv"
        test_file.write_text("data")
        # Files are automatically cleaned up when exiting the context
```

### Code Style and Conventions

- **Python 3.8+**: Ensure compatibility with Python 3.8 and later.
- **Logging**: Use the `logging` module; avoid `print()` for application output.
- **Type hints**: Add type hints to new functions for clarity.
- **Docstrings**: Document public functions and classes with docstrings.
- **Error handling**: Gracefully handle API errors and file I/O failures.

### Common Development Tasks

**Clear logs before testing:**
```bash
truncate -s 0 /tmp/app.log
```

**Run a full workflow with verbose output:**
```bash
python main.py \
  --repo owner/repo \
  --user username \
  --json \
  --analyze \
  --output-csv test_report.csv \
  --generate-report \
  --report-output test_report.md \
  --verbose
```

**Check logs after a run:**
```bash
tail -50 /tmp/app.log
```

**Run specific test with output:**
```bash
pytest tests/test_analyzer.py -v -s
```
