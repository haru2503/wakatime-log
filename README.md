# Trustless WakaTime Logger

**Trustless WakaTime Logger** is a system that automatically logs WakaTime data daily, with one core purpose:
📌 **To make it impossible for *anyone*, including the user themselves, to fake or tamper with the logged data**.

It achieves this by:

* Storing logs in an **immutable** way (once written, cannot be edited).
* Integrating **external verification** or proof mechanisms.
* Promoting full **transparency and integrity** in personal (or public) coding activity tracking.

> The goal is to create a truly **trustless WakaTime logger** – where even the user **can't lie to themselves**, encouraging discipline and honesty.

## Features

* **Trustless Verification**: Multiple external timestamps (NTP, GitHub API, WorldTimeAPI) to prevent data fabrication
* **Structured Organization**: Data organized by year/month/week with automatic folder creation
* **Weekly Summaries**: Automatic generation of weekly summaries with detailed statistics and visualizations
* **Monthly Summaries**: Monthly aggregation of weekly data with charts
* **Data Visualization**: Interactive charts embedded in summary files and standalone visualization tools
* **GitHub Actions**: Automated daily fetching and manual data import workflows

## Folder Structure

```tree
wakatime_logs/
├── 2025/
│   ├── 01_January/
│   │   ├── week_1/
│   │   │   ├── 2025-01-01.json
│   │   │   ├── 2025-01-02.json
│   │   │   ├── ...
│   │   │   ├── week_1.json          # Weekly summary data
│   │   │   └── week_1_summary.md    # Weekly summary report with charts
│   │   ├── week_2/
│   │   ├── ...
│   │   ├── 01_January.json          # Monthly summary data
│   │   └── 01_January_summary.md    # Monthly summary report with charts
│   └── 02_February/
└── 2024/
```

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/haru2503/wakatime-log.git
    cd wakatime-log
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Basic Usage

Run the script to fetch yesterday's data:

```bash
python wakatime_fetcher.py
```

### Advanced Usage

The script automatically:

* Creates folders based on date structure
* Generates week summaries on the first day of a new week (Monday) with embedded charts
* Generates month summaries on the first day of a new month with visualizations
* Fetches 7 days of data when run on Sunday

### GitHub Actions Workflows

This repository includes two GitHub Actions workflows:

#### 1. Daily Fetch Workflow (`log-wakatime.yml`)

**Purpose**: Automatically fetch daily WakaTime data and commit to repository

**Setup**:

1. Go to your repository Settings → Secrets and variables → Actions
2. Add `WAKATIME_API_KEY` secret with your WakaTime API key
3. The workflow runs daily at 1:00 AM UTC

**Features**:

* Fetches yesterday's data automatically
* On the first day of a new week, generates a weekly summary report for the previous week
* On the first day of a new month, generates a monthly summary report for the previous month
* Commits changes to repository with trustless verification

#### 2. Manual Import Workflow (`wakatime-import.yml`)

**Purpose**: Import historical WakaTime data (last N days)

**Setup**:

1. Same API key setup as above
2. Go to Actions tab → "Import WakaTime Data" → "Run workflow"
3. Choose number of days to import (default: 20)

**Features**:

* Import up to 400 days of historical data
* Creates complete folder structure
* Generates all summaries and visualizations
* Perfect for initial setup or data recovery

### Data Visualization

#### Embedded Charts in Summaries

Weekly and monthly summary files (`.md`) now include:

* **Daily Coding Time Bar Chart**: Shows total coding time per day with project breakdown
* **Languages Pie Chart**: Distribution of programming languages
* **Categories Pie Chart**: Distribution of coding categories
* **Editors Pie Chart**: Distribution of code editors used
* **Operating Systems Pie Chart**: Distribution of OS usage
* **Machines Pie Chart**: Distribution of machines used
* **Projects Pie Chart**: Distribution of projects worked on

#### Standalone Visualization Tool

Use the visualizer for custom analysis:

```bash
# Daily coding time chart
python wakatime_visualizer.py --plot-type daily --start-date 2025-01-01 --end-date 2025-01-07

# Languages distribution for a specific date
python wakatime_visualizer.py --plot-type languages --date 2025-01-01

# Editors usage for a specific date
python wakatime_visualizer.py --plot-type editors --date 2025-01-01

# Weekly summary chart
python wakatime_visualizer.py --plot-type weekly --week-folder wakatime_logs/2025/01_January/week_1

# Summary statistics for a date range
python wakatime_visualizer.py --plot-type summary --start-date 2025-01-01 --end-date 2025-01-31
```

## Trustless Verification

The system uses multiple external sources to verify data authenticity:

1. **NTP Timestamps**: Atomic clock time from pool.ntp.org
2. **GitHub API**: Server time from GitHub's servers
3. **WorldTimeAPI**: External time verification
4. **Content Hashing**: SHA-256 hashes of all data
5. **Network Evidence**: Request/response metadata

This makes it impossible to fabricate data without controlling all external verification sources.

## Weekly Summaries

When the script runs on Sunday, it:

1. Fetches data for all 7 days of the week
2. Generates `week_N.json` with aggregated data
3. Creates `week_N_summary.md` with detailed breakdown and charts

### Weekly Summary Contents

* Total coding time for the week
* Daily average coding time
* Total time by categories, languages, projects, editors, machines, OS
* Daily breakdown for each day of the week
* **Embedded Charts**: Bar chart for daily coding time, pie charts for distributions

## Monthly Summaries

On the first day of each month, the script also:

1. Aggregates all weekly summaries for the month
2. Generates `MM_Month.json` with monthly data
3. Creates `MM_Month_summary.md` with monthly breakdown and visualizations

### Monthly Summary Contents

* Total coding time for the month
* Weekly and daily averages
* Total time by categories, languages, projects, editors, machines, OS
* Weekly breakdown for each week of the month
* **Embedded Charts**: Bar chart for weekly coding time, pie charts for distributions

## Folder Creation Rules

* **Month folders**: Created on the first day of each month
* **Week folders**: Created on the first Monday of each month
* **Cross-month weeks**: If a week spans two months, data goes to the week folder in the starting month

## Data Structure

Each daily JSON file contains:

```json
{
  "wakatime_data": {
    "data": [{
      "languages": [...],
      "editors": [...],
      "categories": [...],
      "grand_total": {...}
    }]
  },
  "authenticity_proof": {
    "content_hash": "...",
    "external_timestamps": {...},
    "network_evidence": {...}
  },
  "request_proof": {...},
  "metadata": {...}
}
```

## Verification

To verify the authenticity of any file:

```bash
python wakatime_fetcher.py
# The script will automatically verify the fetched data
```

## Testing

Run the test script to see the folder structure in action:

```bash
python test_structure.py
```

This will create mock data in `test_wakatime_logs/` to demonstrate the structure.

## Automation

### GitHub Actions (Recommended)

The repository includes pre-configured GitHub Actions workflows:

1. **Daily Fetch**: Automatically runs every day at 1:00 AM UTC
2. **Manual Import**: Run on-demand to import historical data

### Manual Cron Job

Set up a cron job to run daily:

```bash
# Daily at 1 AM
0 1 * * * cd /path/to/wakatime-log && python wakatime_fetcher.py
```

## Contributing

Feel free to submit issues and pull requests!!! 🤗

## License

This project is open source and available under the MIT License.
