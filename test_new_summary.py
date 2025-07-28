#!/usr/bin/env python3
"""
Test script to generate new weekly summary with updated charts
"""

import json
from pathlib import Path
from wakatime_charts import WakaTimeCharts
from datetime import datetime


def test_new_weekly_summary():
    """Test generating new weekly summary with lightweight structure"""

    # Load existing week data
    week_folder = Path("wakatime_logs/2025/07_July/week_3")
    week_json_file = week_folder / "week_3.json"

    if not week_json_file.exists():
        print("Week JSON file not found!")
        return

    # Load week data
    with open(week_json_file, "r", encoding="utf-8") as f:
        week_summary_data = json.load(f)

    # Generate charts with new structure
    charts = WakaTimeCharts()
    charts_data = charts.create_weekly_summary_charts(week_summary_data)

    print(f"Generated {len(charts_data)} charts")
    print("Available charts:")
    for chart_name in charts_data.keys():
        print(f"  - {chart_name}")

    # Create new lightweight summary
    md_content = f"""# Week Summary: {week_summary_data['week_dates'][0]} to {week_summary_data['week_dates'][-1]}

## Weekly Totals
- **Total Coding Time**: {format_time_detailed(week_summary_data['total_coding_time'])}
- **Daily Average Coding Time**: {format_time_detailed(week_summary_data['daily_avg_coding_time'])}

## Charts

### Daily Coding Time
"""

    # Add daily coding time chart
    if charts_data.get("daily_coding_time"):
        md_content += f"\n{charts.embed_chart_in_markdown(charts_data['daily_coding_time'], 'Daily Coding Time')}\n"

    # Add weekly aggregated charts
    if charts_data.get("weekly_languages"):
        md_content += "\n### Weekly Languages Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['weekly_languages'], 'Weekly Languages')}\n"

    if charts_data.get("weekly_categories"):
        md_content += "\n### Weekly Categories Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['weekly_categories'], 'Weekly Categories')}\n"

    if charts_data.get("weekly_editors"):
        md_content += "\n### Weekly Editors Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['weekly_editors'], 'Weekly Editors')}\n"

    if charts_data.get("weekly_os"):
        md_content += "\n### Weekly Operating Systems Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['weekly_os'], 'Weekly Operating Systems')}\n"

    if charts_data.get("weekly_machines"):
        md_content += "\n### Weekly Machines Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['weekly_machines'], 'Weekly Machines')}\n"

    if charts_data.get("weekly_projects"):
        md_content += "\n### Weekly Projects Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['weekly_projects'], 'Weekly Projects')}\n"

    md_content += f"""
---
*Generated on: {datetime.now().isoformat()}*
*Days with data: {week_summary_data['metadata']['days_with_data']}/{week_summary_data['metadata']['total_days']}*
"""

    # Save new lightweight summary
    new_summary_file = week_folder / "week_3_summary_lightweight.md"
    with open(new_summary_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\nNew lightweight summary saved: {new_summary_file}")

    # Check file size
    file_size = new_summary_file.stat().st_size
    print(f"File size: {file_size / 1024 / 1024:.2f} MB")

    return new_summary_file


def format_time_detailed(total_seconds):
    """Format seconds to detailed time"""
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    if hours > 0:
        return f"{hours} hrs {minutes} mins ({time_str})"
    else:
        return f"{minutes} mins ({time_str})"


if __name__ == "__main__":
    test_new_weekly_summary()
