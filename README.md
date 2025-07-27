# Trustless WakaTime Logger

A trustless system for logging WakaTime data with external verification to prove authenticity and prevent data fabrication.

## Features

- **Trustless Verification**: Multiple external timestamps (NTP, GitHub API, WorldTimeAPI) to prevent data fabrication
- **Structured Organization**: Data organized by year/month/week with automatic folder creation
- **Weekly Summaries**: Automatic generation of weekly summaries with detailed statistics
- **Monthly Summaries**: Monthly aggregation of weekly data
- **Data Visualization**: Simple charts and statistics for analyzing coding patterns
- **Sunday Special**: On Sundays, fetches 7 days of data and generates week summaries

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
│   │   │   └── week_1_summary.md    # Weekly summary report
│   │   ├── week_2/
│   │   ├── ...
│   │   ├── 01_January.json          # Monthly summary data
│   │   └── 01_January_summary.md    # Monthly summary report
│   └── 02_February/
└── 2024/
```

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd wakatime-log
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Set up your WakaTime API key:

```bash
export WAKATIME_API_KEY='your_api_key_here'
```

## Usage

### Basic Usage

Run the script to fetch yesterday's data:

```bash
python wakatime_fetcher.py
```

### Advanced Usage

The script automatically:

- Creates folders based on date structure
- Generates week summaries on Sundays
- Generates month summaries on the last Sunday of each month
- Fetches 7 days of data when run on Sunday

### Data Visualization

Use the visualizer to create charts and analyze your data:

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
3. Creates `week_N_summary.md` with detailed breakdown

### Weekly Summary Contents

- Total coding time for the week
- Daily average coding time
- Total time by categories, languages, projects, editors, machines, OS
- Daily breakdown for each day of the week

## Monthly Summaries

On the last Sunday of each month, the script also:

1. Aggregates all weekly summaries for the month
2. Generates `MM_Month.json` with monthly data
3. Creates `MM_Month_summary.md` with monthly breakdown

### Monthly Summary Contents

- Total coding time for the month
- Weekly and daily averages
- Total time by categories, languages, projects, editors, machines, OS
- Weekly breakdown for each week of the month

## Folder Creation Rules

- **Month folders**: Created on the first day of each month
- **Week folders**: Created on the first Monday of each month
- **Cross-month weeks**: If a week spans two months, data goes to the week folder in the starting month

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

Set up a cron job or GitHub Actions to run daily:

```bash
# Daily at 1 AM
0 1 * * * cd /path/to/wakatime-log && python wakatime_fetcher.py
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
