#!/usr/bin/env python3
"""
WakaTime Charts Generator
Generate charts for weekly and monthly summaries
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from datetime import datetime
import os
from pathlib import Path
import json
import base64
from io import BytesIO


class WakaTimeCharts:
    def __init__(self):
        # Set style for better looking charts
        plt.style.use("default")
        plt.rcParams["figure.figsize"] = (10, 6)
        plt.rcParams["font.size"] = 10
        plt.rcParams["axes.grid"] = True
        plt.rcParams["grid.alpha"] = 0.3

    def format_time_readable(self, total_seconds):
        """Format seconds to human readable time (e.g., 2h 30m)"""
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def create_daily_coding_time_chart(
        self, daily_summaries, title="Daily Coding Time"
    ):
        """Create a stacked bar chart showing daily coding time with project breakdown"""
        if not daily_summaries:
            return None

        dates = [day["date"] for day in daily_summaries]
        total_times = [day["total_coding_time"] for day in daily_summaries]

        # Get unique projects across all days
        all_projects = set()
        for day in daily_summaries:
            for project in day.get("projects", []):
                all_projects.add(project["name"])

        # Create color map for projects
        colors = plt.cm.Set3(np.linspace(0, 1, len(all_projects)))
        project_colors = {project: colors[i] for i, project in enumerate(all_projects)}

        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(12, 6))

        # Initialize bottom positions
        bottoms = np.zeros(len(dates))

        # Plot each project
        for project in all_projects:
            project_times = []
            for day in daily_summaries:
                project_data = next(
                    (p for p in day.get("projects", []) if p["name"] == project), None
                )
                project_times.append(
                    project_data["total_seconds"] if project_data else 0
                )

            if sum(project_times) > 0:  # Only plot if project has time
                ax.bar(
                    dates,
                    project_times,
                    bottom=bottoms,
                    label=project,
                    color=project_colors[project],
                    alpha=0.8,
                )
                bottoms += np.array(project_times)

        # Customize chart
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Coding Time (hours)")

        # Format y-axis to show hours
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x/3600:.1f}h"))

        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Add legend
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")

        # Add value labels on bars
        for i, (date, total_time) in enumerate(zip(dates, total_times)):
            if total_time > 0:
                ax.text(
                    i,
                    total_time + 0.1,
                    self.format_time_readable(total_time),
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        plt.tight_layout()
        return self._save_chart_to_base64(fig)

    def create_pie_chart(self, items, title, max_items=8):
        """Create a pie chart for languages, categories, editors, etc."""
        if not items:
            return None

        # Sort by total_seconds and take top items
        sorted_items = sorted(
            items, key=lambda x: x.get("total_seconds", 0), reverse=True
        )

        if len(sorted_items) > max_items:
            # Group others
            main_items = sorted_items[: max_items - 1]
            others_total = sum(
                item.get("total_seconds", 0) for item in sorted_items[max_items - 1 :]
            )
            if others_total > 0:
                main_items.append({"name": "Others", "total_seconds": others_total})
            sorted_items = main_items

        # Prepare data
        labels = [item["name"] for item in sorted_items]
        sizes = [item.get("total_seconds", 0) for item in sorted_items]
        total = sum(sizes)

        if total == 0:
            return None

        # Calculate percentages
        percentages = [size / total * 100 for size in sizes]

        # Create pie chart with more space for legend
        fig, ax = plt.subplots(figsize=(12, 8))

        # Create pie chart with custom colors and no labels on pie
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))

        # Only show percentage if it's large enough (>5%)
        def make_autopct(values):
            def my_autopct(pct):
                # Only show percentage if it's > 5%
                if pct > 5:
                    return f"{pct:.1f}%"
                else:
                    return ""

            return my_autopct

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,  # No labels on pie
            autopct=make_autopct(sizes),
            colors=colors,
            startangle=90,
            pctdistance=0.85,
        )

        # Customize percentage text
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontweight("bold")
            autotext.set_fontsize(10)

        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

        # Add total time in the center
        total_time_str = self.format_time_readable(total)
        ax.text(
            0,
            0,
            total_time_str,
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
            transform=ax.transData,
        )

        # Create legend with time and percentage
        legend_labels = []
        for i, (label, size, pct) in enumerate(zip(labels, sizes, percentages)):
            time_str = self.format_time_readable(size)
            if pct > 5:
                legend_labels.append(f"{label} - {time_str} ({pct:.1f}%)")
            else:
                legend_labels.append(f"{label} - {time_str}")

        # Add legend outside the pie chart
        ax.legend(
            wedges,
            legend_labels,
            title="Legend",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=10,
        )

        plt.tight_layout()
        return self._save_chart_to_base64(fig)

    def create_weekly_summary_charts(self, week_summary_data):
        """Create all charts for weekly summary"""
        charts = {}

        # Daily coding time chart
        if week_summary_data.get("daily_summaries"):
            charts["daily_coding_time"] = self.create_daily_coding_time_chart(
                week_summary_data["daily_summaries"], "Weekly Daily Coding Time"
            )

        # Pie charts for each category
        for day_summary in week_summary_data.get("daily_summaries", []):
            # Languages pie chart
            if day_summary.get("languages"):
                charts[f"languages_{day_summary['date']}"] = self.create_pie_chart(
                    day_summary["languages"], f"Languages - {day_summary['date']}"
                )

            # Categories pie chart
            if day_summary.get("categories"):
                charts[f"categories_{day_summary['date']}"] = self.create_pie_chart(
                    day_summary["categories"], f"Categories - {day_summary['date']}"
                )

            # Editors pie chart
            if day_summary.get("editors"):
                charts[f"editors_{day_summary['date']}"] = self.create_pie_chart(
                    day_summary["editors"], f"Editors - {day_summary['date']}"
                )

            # Operating Systems pie chart
            if day_summary.get("operating_systems"):
                charts[f"os_{day_summary['date']}"] = self.create_pie_chart(
                    day_summary["operating_systems"],
                    f"Operating Systems - {day_summary['date']}",
                )

            # Machines pie chart
            if day_summary.get("machines"):
                charts[f"machines_{day_summary['date']}"] = self.create_pie_chart(
                    day_summary["machines"], f"Machines - {day_summary['date']}"
                )

            # Projects pie chart
            if day_summary.get("projects"):
                charts[f"projects_{day_summary['date']}"] = self.create_pie_chart(
                    day_summary["projects"], f"Projects - {day_summary['date']}"
                )

        return charts

    def create_monthly_summary_charts(self, month_summary_data):
        """Create all charts for monthly summary"""
        charts = {}

        # Weekly coding time chart
        if month_summary_data.get("weekly_summaries"):
            weekly_data = []
            for week in month_summary_data["weekly_summaries"]:
                weekly_data.append(
                    {
                        "date": f"Week {week['week'].split('_')[1]}",
                        "total_coding_time": week["total_coding_time"],
                        "projects": [],  # We'll need to aggregate projects from daily data
                    }
                )

            charts["weekly_coding_time"] = self.create_daily_coding_time_chart(
                weekly_data, "Monthly Weekly Coding Time"
            )

        # Aggregate data for pie charts (placeholder for future implementation)
        # total_languages = []
        # total_categories = []
        # total_editors = []
        # total_os = []
        # total_machines = []
        # total_projects = []

        # This would need to be implemented based on the actual data structure
        # For now, we'll create placeholder charts

        return charts

    def _save_chart_to_base64(self, fig):
        """Save chart to base64 string for embedding in markdown"""
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{img_str}"

    def embed_chart_in_markdown(self, chart_base64, alt_text="Chart"):
        """Create markdown image tag for chart"""
        return f"![{alt_text}]({chart_base64})"


def main():
    """Test the charts generator"""
    charts = WakaTimeCharts()

    # Test with sample data
    sample_data = {
        "daily_summaries": [
            {
                "date": "2025-01-01",
                "total_coding_time": 28800,  # 8 hours
                "languages": [
                    {"name": "Python", "total_seconds": 14400, "percent": 50.0},
                    {"name": "JavaScript", "total_seconds": 7200, "percent": 25.0},
                    {"name": "HTML", "total_seconds": 7200, "percent": 25.0},
                ],
                "categories": [
                    {"name": "Coding", "total_seconds": 23040, "percent": 80.0},
                    {"name": "Debugging", "total_seconds": 5760, "percent": 20.0},
                ],
                "projects": [
                    {"name": "Project A", "total_seconds": 14400, "percent": 50.0},
                    {"name": "Project B", "total_seconds": 14400, "percent": 50.0},
                ],
            }
        ]
    }

    charts_data = charts.create_weekly_summary_charts(sample_data)
    print("Charts generated successfully!")
    print(f"Generated {len(charts_data)} charts")


if __name__ == "__main__":
    main()
