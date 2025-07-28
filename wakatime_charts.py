#!/usr/bin/env python3
"""
WakaTime Charts Generator
Generate charts for weekly and monthly summaries
"""

import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from pathlib import Path


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

        # Set y-axis limit to prevent overflow
        max_time = max(total_times) if total_times else 0
        ax.set_ylim(0, max_time * 1.1)  # Add 10% padding

        plt.tight_layout()
        return self._save_chart_to_file(fig, "daily_coding_time")

    def create_daily_stacked_bar_chart(
        self,
        daily_summaries,
        title="Daily Coding Time by Project",
        chart_name="daily_stacked_bar",
    ):
        if not daily_summaries:
            return None

        import matplotlib.pyplot as plt
        import numpy as np
        from datetime import datetime

        dates = [day["date"] for day in daily_summaries]
        # Định dạng ngày cho trục x
        date_labels = [
            datetime.strptime(d, "%Y-%m-%d").strftime("%d-%m-%Y") for d in dates
        ]
        all_projects = sorted(
            {p["name"] for day in daily_summaries for p in day.get("projects", [])}
        )

        # Chuẩn bị dữ liệu: mỗi project là 1 list thời gian theo ngày
        project_times = {project: [] for project in all_projects}
        total_times = []
        for day in daily_summaries:
            projects_today = {
                p["name"]: p["total_seconds"] for p in day.get("projects", [])
            }
            total = sum(projects_today.values())
            total_times.append(total / 3600)  # giờ
            for project in all_projects:
                project_times[project].append(
                    projects_today.get(project, 0) / 3600
                )  # giờ

        fig, ax = plt.subplots(figsize=(max(8, len(dates) * 1.2), 6))
        bottoms = np.zeros(len(dates))
        bar_width = 0.6

        color_map = plt.cm.get_cmap("tab20", len(all_projects))
        for i, project in enumerate(all_projects):
            times = project_times[project]
            ax.bar(
                date_labels,
                times,
                bottom=bottoms,
                label=project,
                width=bar_width,
                color=color_map(i),
            )
            bottoms += np.array(times)

        # Hiển thị tổng thời gian trên đầu mỗi cột
        for i, (x, total) in enumerate(zip(date_labels, total_times)):
            ax.text(
                i,
                bottoms[i] + 0.1,
                f"{total:.2f}h",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        # Đảm bảo cột không bị "đâm thủng" chart
        y_max = max(bottoms) * 1.15 if bottoms.any() else 1
        ax.set_ylim(0, y_max)

        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Coding Time (hours)")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        return self._save_chart_to_file(fig, chart_name)

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

        # Add legend outside the pie chart (without title)
        ax.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=10,
        )

        plt.tight_layout()
        return self._save_chart_to_file(fig, title.lower().replace(" ", "_"))

    def create_weekly_summary_charts(self, week_summary_data, output_dir=None):
        """Create all charts for weekly summary"""
        charts = {}

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

        # Daily coding time chart
        if week_summary_data.get("daily_summaries"):
            chart_file = self.create_daily_coding_time_chart(
                week_summary_data["daily_summaries"], "Weekly Daily Coding Time"
            )
            if chart_file:
                charts["daily_coding_time"] = chart_file
            # Thêm chart stacked bar
            stacked_chart = self.create_daily_stacked_bar_chart(
                week_summary_data["daily_summaries"],
                title="Daily Coding Time by Project (Weekly)",
                chart_name="daily_stacked_bar_weekly",
            )
            if stacked_chart:
                charts["daily_stacked_bar"] = stacked_chart

        # Aggregate data for weekly pie charts
        weekly_languages = self._aggregate_items(week_summary_data, "languages")
        weekly_categories = self._aggregate_items(week_summary_data, "categories")
        weekly_editors = self._aggregate_items(week_summary_data, "editors")
        weekly_os = self._aggregate_items(week_summary_data, "operating_systems")
        weekly_machines = self._aggregate_items(week_summary_data, "machines")
        weekly_projects = self._aggregate_items(week_summary_data, "projects")

        # Create weekly pie charts
        if weekly_languages:
            chart_file = self.create_pie_chart(weekly_languages, "Weekly Languages")
            if chart_file:
                charts["weekly_languages"] = chart_file

        if weekly_categories:
            chart_file = self.create_pie_chart(weekly_categories, "Weekly Categories")
            if chart_file:
                charts["weekly_categories"] = chart_file

        if weekly_editors:
            chart_file = self.create_pie_chart(weekly_editors, "Weekly Editors")
            if chart_file:
                charts["weekly_editors"] = chart_file

        if weekly_os:
            chart_file = self.create_pie_chart(weekly_os, "Weekly Operating Systems")
            if chart_file:
                charts["weekly_os"] = chart_file

        if weekly_machines:
            chart_file = self.create_pie_chart(weekly_machines, "Weekly Machines")
            if chart_file:
                charts["weekly_machines"] = chart_file

        if weekly_projects:
            chart_file = self.create_pie_chart(weekly_projects, "Weekly Projects")
            if chart_file:
                charts["weekly_projects"] = chart_file

        # Daily breakdown charts (for individual days)
        for day_summary in week_summary_data.get("daily_summaries", []):
            # Languages pie chart
            if day_summary.get("languages"):
                chart_file = self.create_pie_chart(
                    day_summary["languages"], f"Languages - {day_summary['date']}"
                )
                if chart_file:
                    charts[f"languages_{day_summary['date']}"] = chart_file

            # Categories pie chart
            if day_summary.get("categories"):
                chart_file = self.create_pie_chart(
                    day_summary["categories"], f"Categories - {day_summary['date']}"
                )
                if chart_file:
                    charts[f"categories_{day_summary['date']}"] = chart_file

            # Editors pie chart
            if day_summary.get("editors"):
                chart_file = self.create_pie_chart(
                    day_summary["editors"], f"Editors - {day_summary['date']}"
                )
                if chart_file:
                    charts[f"editors_{day_summary['date']}"] = chart_file

            # Operating Systems pie chart
            if day_summary.get("operating_systems"):
                chart_file = self.create_pie_chart(
                    day_summary["operating_systems"],
                    f"Operating Systems - {day_summary['date']}",
                )
                if chart_file:
                    charts[f"os_{day_summary['date']}"] = chart_file

            # Machines pie chart
            if day_summary.get("machines"):
                chart_file = self.create_pie_chart(
                    day_summary["machines"], f"Machines - {day_summary['date']}"
                )
                if chart_file:
                    charts[f"machines_{day_summary['date']}"] = chart_file

            # Projects pie chart
            if day_summary.get("projects"):
                chart_file = self.create_pie_chart(
                    day_summary["projects"], f"Projects - {day_summary['date']}"
                )
                if chart_file:
                    charts[f"projects_{day_summary['date']}"] = chart_file

        return charts

    def create_monthly_summary_charts(self, month_summary_data, output_dir=None):
        """Create all charts for monthly summary"""
        charts = {}

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

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

            chart_file = self.create_daily_coding_time_chart(
                weekly_data, "Monthly Weekly Coding Time"
            )
            if chart_file:
                charts["weekly_coding_time"] = chart_file
            # Thêm chart stacked bar cho từng ngày trong tháng
            # Gom daily_summaries của tất cả các tuần
            all_days = []
            for week in month_summary_data["weekly_summaries"]:
                all_days.extend(week.get("daily_summaries", []))
            stacked_chart = self.create_daily_stacked_bar_chart(
                all_days,
                title="Daily Coding Time by Project (Monthly)",
                chart_name="daily_stacked_bar_monthly",
            )
            if stacked_chart:
                charts["daily_stacked_bar"] = stacked_chart

        # Aggregate data for monthly pie charts
        monthly_languages = self._aggregate_items(month_summary_data, "languages")
        monthly_categories = self._aggregate_items(month_summary_data, "categories")
        monthly_editors = self._aggregate_items(month_summary_data, "editors")
        monthly_os = self._aggregate_items(month_summary_data, "operating_systems")
        monthly_machines = self._aggregate_items(month_summary_data, "machines")
        monthly_projects = self._aggregate_items(month_summary_data, "projects")

        # Create monthly pie charts
        if monthly_languages:
            chart_file = self.create_pie_chart(monthly_languages, "Monthly Languages")
            if chart_file:
                charts["monthly_languages"] = chart_file

        if monthly_categories:
            chart_file = self.create_pie_chart(monthly_categories, "Monthly Categories")
            if chart_file:
                charts["monthly_categories"] = chart_file

        if monthly_editors:
            chart_file = self.create_pie_chart(monthly_editors, "Monthly Editors")
            if chart_file:
                charts["monthly_editors"] = chart_file

        if monthly_os:
            chart_file = self.create_pie_chart(monthly_os, "Monthly Operating Systems")
            if chart_file:
                charts["monthly_os"] = chart_file

        if monthly_machines:
            chart_file = self.create_pie_chart(monthly_machines, "Monthly Machines")
            if chart_file:
                charts["monthly_machines"] = chart_file

        if monthly_projects:
            chart_file = self.create_pie_chart(monthly_projects, "Monthly Projects")
            if chart_file:
                charts["monthly_projects"] = chart_file

        return charts

    def _aggregate_items(self, summary_data, item_type):
        """Aggregate items across all days/weeks for pie charts"""
        aggregated = {}

        # Handle daily summaries (for weekly data)
        for day in summary_data.get("daily_summaries", []):
            for item in day.get(item_type, []):
                name = item["name"]
                seconds = item.get("total_seconds", 0)
                if name in aggregated:
                    aggregated[name] += seconds
                else:
                    aggregated[name] = seconds

        # Handle weekly summaries (for monthly data)
        for week in summary_data.get("weekly_summaries", []):
            for day in week.get("daily_summaries", []):
                for item in day.get(item_type, []):
                    name = item["name"]
                    seconds = item.get("total_seconds", 0)
                    if name in aggregated:
                        aggregated[name] += seconds
                    else:
                        aggregated[name] = seconds

        # Convert to list format
        return [
            {"name": name, "total_seconds": seconds}
            for name, seconds in aggregated.items()
            if seconds > 0
        ]

    def _save_chart_to_file(self, fig, chart_name):
        """Save chart to PNG file in charts folder at repo root"""
        from pathlib import Path

        repo_root = Path(__file__).parent.resolve()
        charts_dir = repo_root / "charts"
        charts_dir.mkdir(parents=True, exist_ok=True)
        filename = charts_dir / f"{chart_name}.png"
        fig.savefig(filename, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"[DEBUG] Chart saved to: {filename}")  # Thêm dòng này để debug
        return str(filename)

    def _save_chart_to_base64(self, fig):
        """Save chart to base64 string for embedding in markdown"""
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="png", dpi=150, bbox_inches="tight")
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{img_str}"

    def embed_chart_in_markdown(self, chart_file, alt_text="Chart"):
        """Create markdown image tag for chart file, always use /charts/... absolute path"""
        from pathlib import Path

        chart_path = Path(chart_file)
        # Always use absolute path from repo root
        abs_path = f"/charts/{chart_path.name}"
        return f"![{alt_text}]({abs_path})"


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
    charts = WakaTimeCharts()
    # Dữ liệu mẫu 7 ngày, 3 project
    sample_data = [
        {
            "date": "Mon",
            "projects": [
                {"name": "poker", "total_seconds": 3 * 3600},
                {"name": "cs50", "total_seconds": 4 * 3600},
            ],
        },
        {
            "date": "Tue",
            "projects": [
                {"name": "poker", "total_seconds": 2 * 3600},
                {"name": "cs50", "total_seconds": 5 * 3600},
            ],
        },
        {
            "date": "Wed",
            "projects": [
                {"name": "poker", "total_seconds": 1 * 3600},
                {"name": "cs50", "total_seconds": 2 * 3600},
                {"name": "waka", "total_seconds": 3 * 3600},
            ],
        },
        {
            "date": "Thu",
            "projects": [
                {"name": "poker", "total_seconds": 4 * 3600},
                {"name": "waka", "total_seconds": 2 * 3600},
            ],
        },
        {
            "date": "Fri",
            "projects": [
                {"name": "cs50", "total_seconds": 6 * 3600},
            ],
        },
        {
            "date": "Sat",
            "projects": [
                {"name": "waka", "total_seconds": 5 * 3600},
            ],
        },
        {
            "date": "Sun",
            "projects": [
                {"name": "poker", "total_seconds": 2 * 3600},
                {"name": "cs50", "total_seconds": 2 * 3600},
                {"name": "waka", "total_seconds": 2 * 3600},
            ],
        },
    ]
    charts.create_daily_stacked_bar_chart(
        sample_data, title="Test Stacked Bar Chart", chart_name="test_stacked_bar"
    )
    print("[TEST] Saved test stacked bar chart to charts/test_stacked_bar.png")
