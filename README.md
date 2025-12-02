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
