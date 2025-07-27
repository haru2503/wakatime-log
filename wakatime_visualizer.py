#!/usr/bin/env python3
"""
WakaTime Data Visualizer
Simple script to query and visualize WakaTime data from the structured logs
"""

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pathlib import Path
import argparse
import numpy as np


class WakaTimeVisualizer:
    def __init__(self, base_dir="wakatime_logs"):
        self.base_dir = Path(base_dir)

    def load_daily_data(self, date):
        """Load daily data for a specific date"""
        folder_path = self.get_folder_path(date)
        file_path = folder_path / f"{date.strftime('%Y-%m-%d')}.json"

        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def get_folder_path(self, target_date):
        """Get the folder path for a specific date (same logic as fetcher)"""
        year = target_date.year
        month_num = target_date.month
        month_name = target_date.strftime("%B")
        month_folder = f"{month_num:02d}_{month_name}"

        # Calculate week number
        first_day = target_date.replace(day=1)
        first_monday = first_day + timedelta(days=(7 - first_day.weekday()) % 7)

        if target_date < first_monday:
            week_num = 1
        else:
            week_diff = (target_date - first_monday).days // 7
            week_num = week_diff + 1

        week_folder = f"week_{week_num}"

        return self.base_dir / str(year) / month_folder / week_folder

    def get_coding_time(self, data):
        """Extract total coding time from data"""
        if data and "wakatime_data" in data:
            wakatime_data = data["wakatime_data"]["data"][0]
            return (
                wakatime_data["grand_total"]["total_seconds"] / 3600
            )  # Convert to hours
        return 0

    def get_languages_data(self, data):
        """Extract languages data from daily data"""
        if data and "wakatime_data" in data:
            wakatime_data = data["wakatime_data"]["data"][0]
            return wakatime_data.get("languages", [])
        return []

    def get_editors_data(self, data):
        """Extract editors data from daily data"""
        if data and "wakatime_data" in data:
            wakatime_data = data["wakatime_data"]["data"][0]
            return wakatime_data.get("editors", [])
        return []

    def plot_daily_coding_time(self, start_date, end_date):
        """Plot daily coding time for a date range"""
        dates = []
        coding_times = []

        current_date = start_date
        while current_date <= end_date:
            data = self.load_daily_data(current_date)
            coding_time = self.get_coding_time(data)

            dates.append(current_date)
            coding_times.append(coding_time)

            current_date += timedelta(days=1)

        # Filter out days with no data
        valid_data = [
            (date, time) for date, time in zip(dates, coding_times) if time > 0
        ]

        if not valid_data:
            print("No data found for the specified date range")
            return

        dates, times = zip(*valid_data)

        plt.figure(figsize=(12, 6))
        plt.plot(dates, times, marker="o", linewidth=2, markersize=6)
        plt.fill_between(dates, times, alpha=0.3)

        plt.title(
            f'Daily Coding Time: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
        )
        plt.xlabel("Date")
        plt.ylabel("Coding Time (hours)")
        plt.grid(True, alpha=0.3)

        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    def plot_languages_pie(self, date):
        """Plot languages distribution for a specific date"""
        data = self.load_daily_data(date)
        languages = self.get_languages_data(data)

        if not languages:
            print(f"No language data found for {date.strftime('%Y-%m-%d')}")
            return

        # Prepare data for pie chart
        names = [lang["name"] for lang in languages]
        times = [lang["total_seconds"] / 3600 for lang in languages]  # Convert to hours

        plt.figure(figsize=(10, 8))
        plt.pie(times, labels=names, autopct="%1.1f%%", startangle=90)
        plt.title(f'Languages Distribution: {date.strftime("%Y-%m-%d")}')
        plt.axis("equal")

        # Add legend
        legend_labels = [f"{name}: {time:.1f}h" for name, time in zip(names, times)]
        plt.legend(legend_labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        plt.tight_layout()
        plt.show()

    def plot_editors_bar(self, date):
        """Plot editors usage for a specific date"""
        data = self.load_daily_data(date)
        editors = self.get_editors_data(data)

        if not editors:
            print(f"No editor data found for {date.strftime('%Y-%m-%d')}")
            return

        # Prepare data for bar chart
        names = [editor["name"] for editor in editors]
        times = [
            editor["total_seconds"] / 3600 for editor in editors
        ]  # Convert to hours

        plt.figure(figsize=(10, 6))
        bars = plt.bar(names, times, color="skyblue", alpha=0.7)

        # Add value labels on bars
        for bar, time in zip(bars, times):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{time:.1f}h",
                ha="center",
                va="bottom",
            )

        plt.title(f'Editors Usage: {date.strftime("%Y-%m-%d")}')
        plt.xlabel("Editor")
        plt.ylabel("Usage Time (hours)")
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def plot_weekly_summary(self, week_folder_path):
        """Plot weekly summary from week folder"""
        week_json_file = week_folder_path / f"{week_folder_path.name}.json"

        if not week_json_file.exists():
            print(f"Week summary not found: {week_json_file}")
            return

        with open(week_json_file, "r", encoding="utf-8") as f:
            week_data = json.load(f)

        # Extract daily data
        daily_summaries = week_data["daily_summaries"]

        if not daily_summaries:
            print("No daily data found in week summary")
            return

        dates = [
            datetime.strptime(day["date"], "%Y-%m-%d").date() for day in daily_summaries
        ]
        coding_times = [
            day["total_coding_time"] / 3600 for day in daily_summaries
        ]  # Convert to hours

        plt.figure(figsize=(12, 6))
        bars = plt.bar(dates, coding_times, color="lightgreen", alpha=0.7)

        # Add value labels on bars
        for bar, time in zip(bars, coding_times):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{time:.1f}h",
                ha="center",
                va="bottom",
            )

        plt.title(
            f'Weekly Coding Time: {week_data["week_dates"][0]} to {week_data["week_dates"][-1]}'
        )
        plt.xlabel("Date")
        plt.ylabel("Coding Time (hours)")
        plt.grid(True, alpha=0.3)

        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    def show_summary_stats(self, start_date, end_date):
        """Show summary statistics for a date range"""
        total_coding_time = 0
        days_with_data = 0
        all_languages = {}
        all_editors = {}

        current_date = start_date
        while current_date <= end_date:
            data = self.load_daily_data(current_date)
            if data:
                coding_time = self.get_coding_time(data)
                if coding_time > 0:
                    total_coding_time += coding_time
                    days_with_data += 1

                    # Aggregate languages
                    languages = self.get_languages_data(data)
                    for lang in languages:
                        name = lang["name"]
                        time = lang["total_seconds"] / 3600
                        all_languages[name] = all_languages.get(name, 0) + time

                    # Aggregate editors
                    editors = self.get_editors_data(data)
                    for editor in editors:
                        name = editor["name"]
                        time = editor["total_seconds"] / 3600
                        all_editors[name] = all_editors.get(name, 0) + time

            current_date += timedelta(days=1)

        print(
            f"\n=== Summary Statistics: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ==="
        )
        print(f"Total Coding Time: {total_coding_time:.2f} hours")
        print(f"Days with Data: {days_with_data}")
        if days_with_data > 0:
            print(
                f"Average Daily Coding Time: {total_coding_time/days_with_data:.2f} hours"
            )

        print("\nTop Languages:")
        sorted_languages = sorted(
            all_languages.items(), key=lambda x: x[1], reverse=True
        )
        for lang, time in sorted_languages[:5]:
            print(f"  {lang}: {time:.2f} hours")

        print("\nTop Editors:")
        sorted_editors = sorted(all_editors.items(), key=lambda x: x[1], reverse=True)
        for editor, time in sorted_editors[:5]:
            print(f"  {editor}: {time:.2f} hours")


def main():
    parser = argparse.ArgumentParser(description="WakaTime Data Visualizer")
    parser.add_argument(
        "--base-dir", default="wakatime_logs", help="Base directory for data"
    )
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--date", help="Specific date for pie/bar charts (YYYY-MM-DD)")
    parser.add_argument("--week-folder", help="Week folder path for weekly summary")
    parser.add_argument(
        "--plot-type",
        choices=["daily", "languages", "editors", "weekly", "summary"],
        help="Type of plot to generate",
    )

    args = parser.parse_args()

    visualizer = WakaTimeVisualizer(args.base_dir)

    if args.plot_type == "daily" and args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        visualizer.plot_daily_coding_time(start_date, end_date)

    elif args.plot_type == "languages" and args.date:
        date = datetime.strptime(args.date, "%Y-%m-%d").date()
        visualizer.plot_languages_pie(date)

    elif args.plot_type == "editors" and args.date:
        date = datetime.strptime(args.date, "%Y-%m-%d").date()
        visualizer.plot_editors_bar(date)

    elif args.plot_type == "weekly" and args.week_folder:
        week_folder_path = Path(args.week_folder)
        visualizer.plot_weekly_summary(week_folder_path)

    elif args.plot_type == "summary" and args.start_date and args.end_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        visualizer.show_summary_stats(start_date, end_date)

    else:
        print("Usage examples:")
        print(
            "  python wakatime_visualizer.py --plot-type daily --start-date 2025-01-01 --end-date 2025-01-07"
        )
        print("  python wakatime_visualizer.py --plot-type languages --date 2025-01-01")
        print("  python wakatime_visualizer.py --plot-type editors --date 2025-01-01")
        print(
            "  python wakatime_visualizer.py --plot-type weekly --week-folder wakatime_logs/2025/01_January/week_1"
        )
        print(
            "  python wakatime_visualizer.py --plot-type summary --start-date 2025-01-01 --end-date 2025-01-31"
        )


if __name__ == "__main__":
    main()
