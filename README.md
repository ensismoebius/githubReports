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

Key configuration options include:

*   **GitHub Token**: A personal access token is required for authentication with the GitHub API. This is essential for fetching data, especially from private repositories or to avoid rate limits.
*   **GitHub API URL**: The base URL for the GitHub API (defaults to `https://api.github.com`).
*   **Default Repository**: An optional `owner/repo` string to specify a default repository for analysis.
*   **Scoring Parameters**: Define points for different actions (e.g., `PointsPerCommit`, `PointsPerIssueCreated`, `PointsPerPrApproved`).
*   **Grading Thresholds**: Set score thresholds for different grades (e.g., `MB`, `B`, `R`).
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

