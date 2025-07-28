#!/usr/bin/env python3
"""
Create lightweight summaries with PNG charts
"""

import json
from pathlib import Path
from datetime import datetime
from wakatime_charts import WakaTimeCharts


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


def create_daily_summary(day_date, day_data):
    """Create individual daily summary markdown file"""
    wakatime_data = day_data["wakatime_data"]["data"][0]

    # Generate charts for this day
    charts = WakaTimeCharts()
    daily_summary = {
        "date": day_date.strftime("%Y-%m-%d"),
        "total_coding_time": calculate_total_seconds([wakatime_data["grand_total"]]),
        "categories": wakatime_data.get("categories", []),
        "languages": wakatime_data.get("languages", []),
        "projects": wakatime_data.get("projects", []),
        "editors": wakatime_data.get("editors", []),
        "machines": wakatime_data.get("machines", []),
        "operating_systems": wakatime_data.get("operating_systems", []),
    }

    charts_data = charts.create_weekly_summary_charts(
        {"daily_summaries": [daily_summary]}
    )

    # Create daily summary markdown
    folder_path = get_folder_path(day_date)
    daily_md_file = folder_path / f"{day_date.strftime('%Y-%m-%d')}_summary.md"

    md_content = (
        f"# Daily Summary: {day_date.strftime('%Y-%m-%d')}\n\n"
        f"## Daily Totals\n"
        f"- **Total Coding Time**: {format_time_detailed(daily_summary['total_coding_time'])}\n\n"
        f"## Charts\n\n### Languages Distribution\n"
    )

    if charts_data.get(f"languages_{daily_summary['date']}"):
        md_content += f"{charts.embed_chart_in_markdown(charts_data[f'languages_{daily_summary['date']}'], 'Languages')}\n"

    md_content += "\n### Categories Distribution\n"
    if charts_data.get(f"categories_{daily_summary['date']}"):
        md_content += f"{charts.embed_chart_in_markdown(charts_data[f'categories_{daily_summary['date']}'], 'Categories')}\n"

    md_content += "\n### Editors Distribution\n"
    if charts_data.get(f"editors_{daily_summary['date']}"):
        md_content += f"{charts.embed_chart_in_markdown(charts_data[f'editors_{daily_summary['date']}'], 'Editors')}\n"

    md_content += "\n### Operating Systems Distribution\n"
    if charts_data.get(f"os_{daily_summary['date']}"):
        md_content += f"{charts.embed_chart_in_markdown(charts_data[f'os_{daily_summary['date']}'], 'Operating Systems')}\n"

    md_content += "\n### Machines Distribution\n"
    if charts_data.get(f"machines_{daily_summary['date']}"):
        md_content += f"{charts.embed_chart_in_markdown(charts_data[f'machines_{daily_summary['date']}'], 'Machines')}\n"

    md_content += "\n### Projects Distribution\n"
    if charts_data.get(f"projects_{daily_summary['date']}"):
        md_content += f"{charts.embed_chart_in_markdown(charts_data[f'projects_{daily_summary['date']}'], 'Projects')}\n"

    md_content += f"\n---\n*Generated on: {datetime.now().isoformat()}*\n"

    with open(daily_md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[+] Saved daily summary: {daily_md_file}")
    return daily_md_file


def create_weekly_summary(week_folder_path, week_summary_data):
    """Create lightweight weekly summary with aggregated charts"""
    # Generate charts
    charts = WakaTimeCharts()
    charts_data = charts.create_weekly_summary_charts(week_summary_data)

    # Save as Markdown (lightweight version)
    week_md_file = week_folder_path / f"{week_folder_path.name}_summary.md"

    md_content = (
        f"# Week Summary: {week_summary_data['week_dates'][0]} to "
        f"{week_summary_data['week_dates'][-1]}\n\n"
        f"## Weekly Totals\n"
        f"- **Total Coding Time**: "
        f"{format_time_detailed(week_summary_data['total_coding_time'])}\n"
        f"- **Daily Average Coding Time**: "
        f"{format_time_detailed(week_summary_data['daily_avg_coding_time'])}\n\n"
        f"## Charts\n"
    )

    # Add daily coding time chart

    # Add daily stacked bar chart by project
    if charts_data.get("daily_stacked_bar"):
        md_content += f"\n{charts.embed_chart_in_markdown(charts_data['daily_stacked_bar'], 'Daily Coding Time by Project')}\n"

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

    md_content += (
        f"---\n*Generated on: {datetime.now().isoformat()}*\n"
        f"*Days with data: {week_summary_data['metadata']['days_with_data']}/{week_summary_data['metadata']['total_days']}*\n"
    )

    with open(week_md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[+] Saved weekly summary: {week_md_file}")
    return week_md_file


def create_monthly_summary(month_folder_path, month_summary_data):
    """Create lightweight monthly summary with aggregated charts"""
    # Generate charts
    charts = WakaTimeCharts()
    charts_data = charts.create_monthly_summary_charts(month_summary_data)

    # Save as Markdown (lightweight version)
    month_md_file = month_folder_path / f"{month_folder_path.name}_summary.md"

    md_content = (
        f"# Monthly Summary: {month_summary_data.get('month_name', 'Unknown Month')}\n\n"
        f"## Monthly Totals\n"
        f"- **Total Coding Time**: "
        f"{format_time_detailed(month_summary_data.get('total_coding_time', 0))}\n"
        f"- **Weekly Average Coding Time**: "
        f"{format_time_detailed(month_summary_data.get('weekly_avg_coding_time', 0))}\n\n"
        f"## Charts\n\n### Weekly Coding Time\n"
    )

    # Add weekly coding time chart

    # Add daily stacked bar chart by project (monthly)
    if charts_data.get("daily_stacked_bar"):
        md_content += f"\n{charts.embed_chart_in_markdown(charts_data['daily_stacked_bar'], 'Daily Coding Time by Project (Monthly)')}\n"

    # Add monthly aggregated charts
    if charts_data.get("monthly_languages"):
        md_content += "\n### Monthly Languages Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['monthly_languages'], 'Monthly Languages')}\n"

    if charts_data.get("monthly_categories"):
        md_content += "\n### Monthly Categories Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['monthly_categories'], 'Monthly Categories')}\n"

    if charts_data.get("monthly_editors"):
        md_content += "\n### Monthly Editors Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['monthly_editors'], 'Monthly Editors')}\n"

    if charts_data.get("monthly_os"):
        md_content += "\n### Monthly Operating Systems Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['monthly_os'], 'Monthly Operating Systems')}\n"

    if charts_data.get("monthly_machines"):
        md_content += "\n### Monthly Machines Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['monthly_machines'], 'Monthly Machines')}\n"

    if charts_data.get("monthly_projects"):
        md_content += "\n### Monthly Projects Distribution\n"
        md_content += f"{charts.embed_chart_in_markdown(charts_data['monthly_projects'], 'Monthly Projects')}\n"

    md_content += f"""
---
*Generated on: {datetime.now().isoformat()}*
"""

    with open(month_md_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[+] Saved monthly summary: {month_md_file}")
    return month_md_file


def calculate_total_seconds(items):
    """Calculate total seconds from a list of items"""
    return sum(item.get("total_seconds", 0) for item in items)


def get_folder_path(target_date):
    """Get the folder path for a specific date"""
    from datetime import timedelta
    import calendar

    def get_week_number(target_date):
        """Get week number within the month (1-5)"""
        first_day = target_date.replace(day=1)
        first_monday = first_day + timedelta(days=(7 - first_day.weekday()) % 7)

        if target_date < first_monday:
            return 1

        week_diff = (target_date - first_monday).days // 7
        return week_diff + 1

    def get_week_folder_name(target_date):
        """Get week folder name like 'week_1', 'week_2' etc."""
        week_num = get_week_number(target_date)
        return f"week_{week_num}"

    def get_month_folder_name(target_date):
        """Get month folder name like '01_January', '02_February' etc."""
        month_num = target_date.month
        month_name = calendar.month_name[month_num]
        return f"{month_num:02d}_{month_name}"

    year = target_date.year
    month_folder = get_month_folder_name(target_date)
    week_folder = get_week_folder_name(target_date)

    return Path("wakatime_logs") / str(year) / month_folder / week_folder


def main():
    """Create summaries for existing data"""
    print("[*] Creating summaries for existing data...")

    wakatime_logs = Path("wakatime_logs")
    if not wakatime_logs.exists():
        print("wakatime_logs directory not found!")
        return

    today = datetime.now().date()
    # Xác định tháng hiện tại
    current_month = today.month
    current_year = today.year

    for year_dir in wakatime_logs.iterdir():
        if not year_dir.is_dir():
            continue
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir():
                continue
            # Chỉ tạo monthly summary cho tháng đã kết thúc
            month_num = int(month_dir.name.split("_")[0])
            year_num = int(year_dir.name)
            if (year_num > current_year) or (
                year_num == current_year and month_num >= current_month
            ):
                continue
            # Tạo monthly summary nếu có dữ liệu
            month_json_file = month_dir / f"{month_dir.name}.json"
            if month_json_file.exists():
                with open(month_json_file, "r", encoding="utf-8") as f:
                    month_summary_data = json.load(f)
                create_monthly_summary(month_dir, month_summary_data)
            # Xử lý các week như cũ
            for week_dir in month_dir.iterdir():
                if not week_dir.is_dir() or not week_dir.name.startswith("week_"):
                    continue
                week_json_file = week_dir / f"{week_dir.name}.json"
                if not week_json_file.exists():
                    continue
                with open(week_json_file, "r", encoding="utf-8") as f:
                    week_summary_data = json.load(f)
                week_dates = week_summary_data.get("week_dates", [])
                if not week_dates or len(week_dates) < 7:
                    continue  # skip incomplete week
                week_end = datetime.strptime(week_dates[-1], "%Y-%m-%d").date()
                if today <= week_end:
                    continue
                create_weekly_summary(week_dir, week_summary_data)
                for day_summary in week_summary_data.get("daily_summaries", []):
                    day_file = week_dir / f"{day_summary['date']}.json"
                    if day_file.exists():
                        with open(day_file, "r", encoding="utf-8") as f:
                            day_data = json.load(f)
                        day_date = datetime.strptime(
                            day_summary["date"], "%Y-%m-%d"
                        ).date()
                        create_daily_summary(day_date, day_data)
    print("\n[+] Summary creation completed!")


if __name__ == "__main__":
    main()
