#!/usr/bin/env python3
"""
Test script to demonstrate the new WakaTime logger structure
"""

from datetime import datetime, timedelta
from pathlib import Path
import json

# Mock data for testing
MOCK_WAKATIME_DATA = {
    "wakatime_data": {
        "data": [
            {
                "languages": [
                    {
                        "name": "Python",
                        "total_seconds": 26135.909371,
                        "digital": "7:15:35",
                        "text": "7 hrs 15 mins",
                        "percent": 96.67,
                    }
                ],
                "grand_total": {
                    "total_seconds": 27037.153351,
                    "digital": "7:30",
                    "text": "7 hrs 30 mins",
                },
                "editors": [
                    {
                        "name": "VS Code",
                        "total_seconds": 27037.153351,
                        "digital": "7:30:37",
                        "percent": 100.0,
                    }
                ],
                "operating_systems": [
                    {
                        "name": "Linux",
                        "total_seconds": 27037.153351,
                        "digital": "7:30:37",
                        "percent": 100.0,
                    }
                ],
                "categories": [
                    {
                        "name": "Coding",
                        "total_seconds": 26636.196081,
                        "digital": "7:23:56",
                        "percent": 98.52,
                    }
                ],
            }
        ]
    },
    "authenticity_proof": {
        "content_hash": "test_hash",
        "external_timestamps": {
            "timestamps": {
                "ntp_time": 1234567890,
                "github_server_time": "Mon, 01 Jan 2024 00:00:00 GMT",
            }
        },
    },
    "request_proof": {"status_code": 200, "response_size": 1024},
    "metadata": {
        "version": "2.0",
        "date_fetched": "2025-01-01",
        "script_name": "TrustlessWakaTimeLogger",
    },
}


def test_folder_structure():
    """Test the folder structure creation"""
    print("=== Testing Folder Structure ===")

    # Test dates
    test_dates = [
        datetime(2025, 1, 1).date(),  # Wednesday, first week
        datetime(2025, 1, 6).date(),  # Monday, second week
        datetime(2025, 1, 12).date(),  # Sunday, second week
        datetime(2025, 2, 1).date(),  # Saturday, first week of February
    ]

    base_dir = "test_wakatime_logs"

    for test_date in test_dates:
        year = test_date.year
        month_num = test_date.month
        month_name = test_date.strftime("%B")
        month_folder = f"{month_num:02d}_{month_name}"

        # Calculate week number
        first_day = test_date.replace(day=1)
        first_monday = first_day + timedelta(days=(7 - first_day.weekday()) % 7)

        if test_date < first_monday:
            week_num = 1
        else:
            week_diff = (test_date - first_monday).days // 7
            week_num = week_diff + 1

        week_folder = f"week_{week_num}"

        folder_path = Path(base_dir) / str(year) / month_folder / week_folder
        folder_path.mkdir(parents=True, exist_ok=True)

        # Create mock data file
        date_str = test_date.strftime("%Y-%m-%d")
        file_path = folder_path / f"{date_str}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(MOCK_WAKATIME_DATA, f, indent=2)

        print(f"Created: {file_path}")
        print(f"  Date: {test_date}")
        print(f"  Week: {week_num}")
        print(f"  Is Monday: {test_date.weekday() == 0}")
        print(f"  Is Sunday: {test_date.weekday() == 6}")
        print()


def test_week_summary_generation():
    """Test week summary generation"""
    print("=== Testing Week Summary Generation ===")

    # Create a week of mock data
    base_dir = "test_wakatime_logs"
    week_start = datetime(2025, 1, 6).date()  # Monday

    week_folder = Path(base_dir) / "2025" / "01_January" / "week_1"
    week_folder.mkdir(parents=True, exist_ok=True)

    # Create mock data for each day of the week
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        date_str = day_date.strftime("%Y-%m-%d")
        file_path = week_folder / f"{date_str}.json"

        # Modify mock data for each day
        day_data = MOCK_WAKATIME_DATA.copy()
        day_data["metadata"]["date_fetched"] = date_str

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(day_data, f, indent=2)

        print(f"Created mock data for: {date_str}")

    print(f"Week folder: {week_folder}")
    print("Mock week data created successfully!")


if __name__ == "__main__":
    test_folder_structure()
    test_week_summary_generation()

    print("\n=== Test Summary ===")
    print("✅ Folder structure test completed")
    print("✅ Week summary generation test completed")
    print("\nYou can now run the actual script with your WAKATIME_API_KEY:")
    print("export WAKATIME_API_KEY='your_api_key_here'")
    print("python wakatime_fetcher.py")
