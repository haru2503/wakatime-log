#!/usr/bin/env python3
"""
Test script to demonstrate the new detailed format
"""

# No imports needed for this test

# Mock data based on the actual WakaTime structure
MOCK_DAILY_DATA = {
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
                    },
                    {
                        "name": "JSON",
                        "total_seconds": 420.414285,
                        "digital": "0:07:00",
                        "text": "7 mins",
                        "percent": 1.55,
                    },
                    {
                        "name": "Markdown",
                        "total_seconds": 154.48485,
                        "digital": "0:02:34",
                        "text": "2 mins",
                        "percent": 0.57,
                    },
                ],
                "categories": [
                    {
                        "name": "Coding",
                        "total_seconds": 26636.196081,
                        "digital": "7:23:56",
                        "text": "7 hrs 23 mins",
                        "percent": 98.52,
                    },
                    {
                        "name": "AI Coding",
                        "total_seconds": 400.95727,
                        "digital": "0:06:40",
                        "text": "6 mins",
                        "percent": 1.48,
                    },
                ],
                "editors": [
                    {
                        "name": "VS Code",
                        "total_seconds": 27037.153351,
                        "digital": "7:30:37",
                        "text": "7 hrs 30 mins",
                        "percent": 100.0,
                    }
                ],
                "operating_systems": [
                    {
                        "name": "Linux",
                        "total_seconds": 27037.153351,
                        "digital": "7:30:37",
                        "text": "7 hrs 30 mins",
                        "percent": 100.0,
                    }
                ],
                "projects": [
                    {
                        "name": "wakatime-log",
                        "total_seconds": 27037.153351,
                        "digital": "7:30:37",
                        "text": "7 hrs 30 mins",
                        "percent": 100.0,
                    }
                ],
                "grand_total": {
                    "total_seconds": 27037.153351,
                    "digital": "7:30",
                    "text": "7 hrs 30 mins",
                },
            }
        ]
    }
}


def format_time_readable(total_seconds):
    """Format seconds to human readable time (e.g., 2h 30m)"""
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def format_breakdown(items, title):
    """Format breakdown of items with time and percentage"""
    if not items:
        return f"**{title}**: No data"

    # Sort by total_seconds descending
    sorted_items = sorted(items, key=lambda x: x.get("total_seconds", 0), reverse=True)

    breakdown_lines = [f"**{title}**:", ""]

    for item in sorted_items:
        name = item["name"]
        total_seconds = item.get("total_seconds", 0)
        percent = item.get("percent", 0)
        time_str = format_time_readable(total_seconds)

        breakdown_lines.append(f"  {name} - {time_str} ({percent:.2f}%)")

    return "\n".join(breakdown_lines)


def test_format():
    """Test the new format"""
    print("=== Testing New Detailed Format ===\n")

    wakatime_data = MOCK_DAILY_DATA["wakatime_data"]["data"][0]

    print("**Sample Daily Data:**")
    print("Date: 2025-01-01")
    print("Total Coding Time: 07:30:00")
    print()

    print(format_breakdown(wakatime_data.get("languages", []), "Languages"))
    print()

    print(format_breakdown(wakatime_data.get("categories", []), "Categories"))
    print()

    print(format_breakdown(wakatime_data.get("editors", []), "Editors"))
    print()

    print(
        format_breakdown(
            wakatime_data.get("operating_systems", []), "Operating Systems"
        )
    )
    print()

    print(format_breakdown(wakatime_data.get("projects", []), "Projects"))
    print()


if __name__ == "__main__":
    test_format()
