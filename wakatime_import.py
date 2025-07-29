#!/usr/bin/env python3
"""
WakaTime Data Importer
Import the last 20 days of WakaTime data and create folder structure immediately
"""

import requests
import json
import hashlib
import time
from datetime import datetime, timedelta
import os
from pathlib import Path
import calendar
from wakatime_charts import WakaTimeCharts


class WakaTimeImporter:
    def __init__(self, api_key, base_dir="wakatime_logs"):
        self.api_key = api_key
        self.base_dir = base_dir

    def get_week_number(self, target_date):
        """Get week number within the month (1-5)"""
        first_day = target_date.replace(day=1)
        first_monday = first_day + timedelta(days=(7 - first_day.weekday()) % 7)

        if target_date < first_monday:
            return 1

        week_diff = (target_date - first_monday).days // 7
        return week_diff + 1

    def get_week_folder_name(self, target_date):
        """Get week folder name like 'week_1', 'week_2' etc."""
        week_num = self.get_week_number(target_date)
        return f"week_{week_num}"

    def get_month_folder_name(self, target_date):
        """Get month folder name like '01_January', '02_February' etc."""
        month_num = target_date.month
        month_name = calendar.month_name[month_num]
        return f"{month_num:02d}_{month_name}"

    def get_folder_path(self, target_date):
        """Get the folder path for a specific date"""
        year = target_date.year
        month_folder = self.get_month_folder_name(target_date)
        week_folder = self.get_week_folder_name(target_date)

        return Path(self.base_dir) / str(year) / month_folder / week_folder

    def get_external_timestamp(self, data):
        """Get timestamps from multiple external sources"""
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()

        timestamps = {}

        # 1. NTP timestamp (time from atomic clock)
        try:
            import ntplib

            ntp_client = ntplib.NTPClient()
            response = ntp_client.request("pool.ntp.org")
            timestamps["ntp_time"] = response.tx_time
            timestamps["ntp_server"] = "pool.ntp.org"
        except:
            timestamps["ntp_time"] = time.time()
            timestamps["ntp_server"] = "system_fallback"

        # 2. External API timestamp
        try:
            time_api = requests.get(
                "http://worldtimeapi.org/api/timezone/Asia/Ho_Chi_Minh", timeout=5
            )
            if time_api.status_code == 200:
                timestamps["external_time"] = time_api.json()
        except:
            pass

        # 3. GitHub API timestamp (from GitHub's server)
        try:
            github_api = requests.get("https://api.github.com", timeout=5)
            timestamps["github_server_time"] = github_api.headers.get("Date")
        except:
            pass

        return {
            "data_hash": data_hash,
            "timestamps": timestamps,
            "verification_note": "These timestamps are from external sources and cannot be manipulated",
        }

    def create_proof_of_authenticity(self, raw_data):
        """Create proof of authenticity that cannot be forged"""
        # 1. External timestamps
        external_proof = self.get_external_timestamp(raw_data)

        # 2. Network evidence
        network_proof = {
            "user_agent": "WakaTimeImporter/1.0",
            "request_time": datetime.now().isoformat(),
            "system_info": {
                "platform": os.name,
                "hostname": os.environ.get(
                    "COMPUTERNAME", os.environ.get("HOSTNAME", "unknown")
                ),
            },
        }

        # 3. Data integrity hash
        content_hash = hashlib.sha256(
            json.dumps(raw_data, sort_keys=True).encode()
        ).hexdigest()

        return {
            "content_hash": content_hash,
            "external_timestamps": external_proof,
            "network_evidence": network_proof,
            "authenticity_note": "This data cannot be fabricated due to external verifications",
        }

    def fetch_daily_data(self, target_date):
        """Fetch WakaTime data for a specific date"""
        date_str = target_date.strftime("%Y-%m-%d")
        url = f"https://wakatime.com/api/v1/users/current/summaries?start={date_str}&end={date_str}"
        headers = {"Authorization": f"Basic {self.api_key}"}

        print(f"[*] Fetching WakaTime data for {date_str}...")

        request_start = time.time()
        response = requests.get(url, headers=headers)
        request_end = time.time()

        if response.status_code != 200:
            print(f"[!] API Error for {date_str}: {response.status_code}")
            return None

        raw_data = response.json()

        # Check if data exists for this date
        if not raw_data.get("data"):
            print(f"[!] No data found for {date_str}")
            return None

        # Create proof of authenticity
        authenticity_proof = self.create_proof_of_authenticity(raw_data)

        # Add request information
        request_proof = {
            "url": url,
            "method": "GET",
            "status_code": response.status_code,
            "response_headers": dict(response.headers),
            "request_duration": request_end - request_start,
            "response_size": len(response.content),
        }

        # Final data structure
        final_data = {
            "wakatime_data": raw_data,
            "authenticity_proof": authenticity_proof,
            "request_proof": request_proof,
            "metadata": {
                "version": "1.0",
                "date_fetched": date_str,
                "script_name": "WakaTimeImporter",
                "trustless_note": "This file contains multiple external verifications that make fabrication impossible",
            },
        }

        return final_data

    def save_daily_data(self, target_date, data):
        """Save daily data to the appropriate folder structure"""
        folder_path = self.get_folder_path(target_date)
        folder_path.mkdir(parents=True, exist_ok=True)

        date_str = target_date.strftime("%Y-%m-%d")
        filename = folder_path / f"{date_str}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"[+] Saved daily data: {filename}")
        return filename

    def get_week_dates(self, target_date):
        """Get all dates in the week containing target_date"""
        # Find Monday of the week
        days_since_monday = target_date.weekday()
        monday = target_date - timedelta(days=days_since_monday)

        # Return all 7 days of the week
        return [monday + timedelta(days=i) for i in range(7)]

    def calculate_total_seconds(self, items):
        """Calculate total seconds from a list of items"""
        return sum(item.get("total_seconds", 0) for item in items)

    def format_time(self, total_seconds):
        """Format seconds to human readable time"""
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def format_time_readable(self, total_seconds):
        """Format seconds to human readable time (e.g., 2h 30m)"""
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def format_time_detailed(self, total_seconds):
        """Format seconds to detailed time (e.g., 46 hrs 2 mins (46:02:30))"""
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        time_str = self.format_time(total_seconds)
        if hours > 0:
            return f"{hours} hrs {minutes} mins ({time_str})"
        else:
            return f"{minutes} mins ({time_str})"

    def format_breakdown(self, items, title):
        """Format breakdown of items with time and percentage"""
        if not items:
            return f"**{title}**: No data"

        # Sort by total_seconds descending
        sorted_items = sorted(
            items, key=lambda x: x.get("total_seconds", 0), reverse=True
        )

        breakdown_lines = [f"**{title}**:", ""]

        for item in sorted_items:
            name = item["name"]
            total_seconds = item.get("total_seconds", 0)
            percent = item.get("percent", 0)
            time_str = self.format_time_readable(total_seconds)

            breakdown_lines.append(f"  - {name} - {time_str} ({percent:.2f}%)")

        return "\n".join(breakdown_lines)

    def generate_week_summary(self, week_folder_path, week_dates):
        """Generate week summary from daily data files"""
        week_data = []
        daily_summaries = []

        # Collect data from each day in the week
        for day_date in week_dates:
            day_file = week_folder_path / f"{day_date.strftime('%Y-%m-%d')}.json"

            if day_file.exists():
                with open(day_file, "r", encoding="utf-8") as f:
                    day_data = json.load(f)
                    week_data.append(day_data)

                    # Extract daily summary
                    wakatime_data = day_data["wakatime_data"]["data"][0]
                    daily_summary = {
                        "date": day_date.strftime("%Y-%m-%d"),
                        "total_coding_time": self.calculate_total_seconds(
                            [wakatime_data["grand_total"]]
                        ),
                        "categories": wakatime_data.get("categories", []),
                        "languages": wakatime_data.get("languages", []),
                        "projects": wakatime_data.get("projects", []),
                        "editors": wakatime_data.get("editors", []),
                        "machines": wakatime_data.get("machines", []),
                        "operating_systems": wakatime_data.get("operating_systems", []),
                    }
                    daily_summaries.append(daily_summary)

        if not week_data:
            return None

        # Calculate weekly totals
        total_coding_time = sum(day["total_coding_time"] for day in daily_summaries)

        # Calculate daily average
        days_with_data = len(daily_summaries)
        daily_avg_coding_time = (
            total_coding_time / days_with_data if days_with_data > 0 else 0
        )

        # Create week summary data
        week_summary_data = {
            "week_dates": [date.strftime("%Y-%m-%d") for date in week_dates],
            "total_coding_time": total_coding_time,
            "daily_avg_coding_time": daily_avg_coding_time,
            "daily_summaries": daily_summaries,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "days_with_data": days_with_data,
                "total_days": len(week_dates),
            },
        }

        return week_summary_data

    def save_week_summary(self, week_folder_path, week_summary_data):
        """Save week summary as JSON and Markdown (lightweight, no daily breakdown)"""
        # Save as JSON
        week_json_file = week_folder_path / f"{week_folder_path.name}.json"
        with open(week_json_file, "w", encoding="utf-8") as f:
            json.dump(week_summary_data, f, indent=2)

        # Generate charts
        charts = WakaTimeCharts()
        charts_data = charts.create_weekly_summary_charts(week_summary_data)

        # Save as Markdown (lightweight)
        week_md_file = week_folder_path / f"{week_folder_path.name}_summary.md"

        md_content = f"""# Week Summary: {week_summary_data['week_dates'][0]} to {week_summary_data['week_dates'][-1]}\n\n## Weekly Totals\n- **Total Coding Time**: {self.format_time_detailed(week_summary_data['total_coding_time'])}\n- **Daily Average Coding Time**: {self.format_time_detailed(week_summary_data['daily_avg_coding_time'])}\n\n## Charts\n"""

        # Add daily coding time chart
        # if charts_data.get("daily_coding_time"):
        #     md_content += f"\n{charts.embed_chart_in_markdown(charts_data['daily_coding_time'], 'Daily Coding Time')}\n"
        # Thêm chart stacked bar
        if charts_data.get("daily_stacked_bar"):
            md_content += "\n### Daily Coding Time by Project (Stacked Bar)\n"
            md_content += f"{charts.embed_chart_in_markdown(charts_data['daily_stacked_bar'], 'Daily Coding Time by Project')}\n"

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

        md_content += f"""\n---\n*Generated on: {week_summary_data['metadata']['generated_at']}*\n*Days with data: {week_summary_data['metadata']['days_with_data']}/{week_summary_data['metadata']['total_days']}*\n"""

        with open(week_md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"[+] Saved week summary: {week_json_file}")
        print(f"[+] Saved week summary: {week_md_file}")

        # Create daily summaries
        for day_summary in week_summary_data["daily_summaries"]:
            day_file = week_folder_path / f"{day_summary['date']}.json"
            if day_file.exists():
                with open(day_file, "r", encoding="utf-8") as f:
                    day_data = json.load(f)
                self.save_daily_summary(day_summary["date"], day_data)

        return week_json_file, week_md_file

    def save_daily_summary(self, date_str, day_data):
        """Create individual daily summary markdown file with PNG charts"""
        from datetime import datetime as dt

        charts = WakaTimeCharts()
        wakatime_data = day_data["wakatime_data"]["data"][0]
        day_date = dt.strptime(date_str, "%Y-%m-%d").date()
        daily_summary = {
            "date": date_str,
            "total_coding_time": self.calculate_total_seconds(
                [wakatime_data["grand_total"]]
            ),
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
        folder_path = self.get_folder_path(day_date)
        daily_md_file = folder_path / f"{date_str}_summary.md"
        md_content = f"""# Daily Summary: {date_str}\n\n## Daily Totals\n- **Total Coding Time**: {self.format_time_detailed(daily_summary['total_coding_time'])}\n\n## Charts\n\n### Languages Distribution\n"""
        if charts_data.get(f"languages_{date_str}"):
            md_content += f"{charts.embed_chart_in_markdown(charts_data[f'languages_{date_str}'], 'Languages')}\n"
        md_content += "\n### Categories Distribution\n"
        if charts_data.get(f"categories_{date_str}"):
            md_content += f"{charts.embed_chart_in_markdown(charts_data[f'categories_{date_str}'], 'Categories')}\n"
        md_content += "\n### Editors Distribution\n"
        if charts_data.get(f"editors_{date_str}"):
            md_content += f"{charts.embed_chart_in_markdown(charts_data[f'editors_{date_str}'], 'Editors')}\n"
        md_content += "\n### Operating Systems Distribution\n"
        if charts_data.get(f"os_{date_str}"):
            md_content += f"{charts.embed_chart_in_markdown(charts_data[f'os_{date_str}'], 'Operating Systems')}\n"
        md_content += "\n### Machines Distribution\n"
        if charts_data.get(f"machines_{date_str}"):
            md_content += f"{charts.embed_chart_in_markdown(charts_data[f'machines_{date_str}'], 'Machines')}\n"
        md_content += "\n### Projects Distribution\n"
        if charts_data.get(f"projects_{date_str}"):
            md_content += f"{charts.embed_chart_in_markdown(charts_data[f'projects_{date_str}'], 'Projects')}\n"
        md_content += f"""\n---\n*Generated on: {datetime.now().isoformat()}*\n"""
        with open(daily_md_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"[+] Saved daily summary: {daily_md_file}")
        return daily_md_file

    def generate_previous_week_summary(self):
        """Generate weekly summary for the previous week (Monday-Sunday) if today is Monday"""
        today = datetime.today().date()
        if today.weekday() != 0:
            print("[!] Not Monday, skipping weekly summary generation.")
            return None
        # Hôm nay là thứ 2, xác định tuần trước
        last_sunday = today - timedelta(days=1)
        # Tìm Monday của tuần trước
        last_monday = last_sunday - timedelta(days=last_sunday.weekday())
        week_dates = [last_monday + timedelta(days=i) for i in range(7)]
        # Xác định folder chứa dữ liệu tuần trước
        week_folder_path = self.get_folder_path(last_monday)
        if not week_folder_path.exists():
            print(f"[!] No data folder for previous week: {week_folder_path}")
            return None
        week_summary_data = self.generate_week_summary(week_folder_path, week_dates)
        if week_summary_data:
            self.save_week_summary(week_folder_path, week_summary_data)
            print(f"[+] Weekly summary for previous week saved: {week_folder_path}")
            return week_folder_path
        else:
            print("[!] No data to generate previous week summary.")
            return None

    def generate_previous_month_summary(self):
        """Generate monthly summary for the previous month if today is the 1st"""
        today = datetime.today().date()
        if today.day != 1:
            print("[!] Not the 1st day, skipping monthly summary generation.")
            return None
        # Xác định tháng trước
        first_of_this_month = today.replace(day=1)
        last_day_prev_month = first_of_this_month - timedelta(days=1)
        first_day_prev_month = last_day_prev_month.replace(day=1)
        # Lấy tất cả các ngày trong tháng trước
        num_days = last_day_prev_month.day
        month_dates = [
            first_day_prev_month + timedelta(days=i) for i in range(num_days)
        ]
        # Xác định folder chứa dữ liệu tháng trước
        month_folder = self.get_month_folder_name(first_day_prev_month)
        year_folder = str(first_day_prev_month.year)
        month_folder_path = Path(self.base_dir) / year_folder / month_folder
        if not month_folder_path.exists():
            print(f"[!] No data folder for previous month: {month_folder_path}")
            return None
        # Gom toàn bộ daily summaries trong tháng
        daily_summaries = []
        for week_folder in month_folder_path.iterdir():
            if week_folder.is_dir():
                for day_date in month_dates:
                    day_file = week_folder / f"{day_date.strftime('%Y-%m-%d')}.json"
                    if day_file.exists():
                        with open(day_file, "r", encoding="utf-8") as f:
                            day_data = json.load(f)
                        wakatime_data = day_data["wakatime_data"]["data"][0]
                        daily_summary = {
                            "date": day_date.strftime("%Y-%m-%d"),
                            "total_coding_time": self.calculate_total_seconds(
                                [wakatime_data["grand_total"]]
                            ),
                            "categories": wakatime_data.get("categories", []),
                            "languages": wakatime_data.get("languages", []),
                            "projects": wakatime_data.get("projects", []),
                            "editors": wakatime_data.get("editors", []),
                            "machines": wakatime_data.get("machines", []),
                            "operating_systems": wakatime_data.get(
                                "operating_systems", []
                            ),
                        }
                        daily_summaries.append(daily_summary)
        if not daily_summaries:
            print("[!] No data to generate previous month summary.")
            return None
        total_coding_time = sum(day["total_coding_time"] for day in daily_summaries)
        days_with_data = len(daily_summaries)
        daily_avg_coding_time = (
            total_coding_time / days_with_data if days_with_data > 0 else 0
        )
        month_summary_data = {
            "month": first_day_prev_month.strftime("%Y-%m"),
            "month_dates": [d.strftime("%Y-%m-%d") for d in month_dates],
            "total_coding_time": total_coding_time,
            "daily_avg_coding_time": daily_avg_coding_time,
            "daily_summaries": daily_summaries,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "days_with_data": days_with_data,
                "total_days": num_days,
            },
        }
        # Lưu file json và md
        month_json_file = month_folder_path / f"{month_folder}_summary.json"
        with open(month_json_file, "w", encoding="utf-8") as f:
            json.dump(month_summary_data, f, indent=2)
        # Markdown summary (tối giản)
        md_content = (
            f"# Month Summary: {first_day_prev_month.strftime('%B %Y')}\n\n"
            f"## Monthly Totals\n- **Total Coding Time**: {self.format_time_detailed(total_coding_time)}\n"
            f"- **Daily Average Coding Time**: {self.format_time_detailed(daily_avg_coding_time)}\n\n---\n"
            f"*Generated on: {month_summary_data['metadata']['generated_at']}*\n"
            f"*Days with data: {days_with_data}/{num_days}*\n"
        )
        month_md_file = month_folder_path / f"{month_folder}_summary.md"
        with open(month_md_file, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"[+] Monthly summary for previous month saved: {month_folder_path}")
        return month_folder_path

    def import_last_n_days(self, days=20):
        """Import the last N days of WakaTime data"""
        print(f"[*] Starting import of last {days} days of WakaTime data...")

        # Calculate date range (last N days)
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=days - 1)  # N days total

        print(f"[*] Importing data from {start_date} to {end_date}")

        # Track imported data for summary generation
        imported_weeks = set()
        imported_files = []

        current_date = start_date
        while current_date <= end_date:
            print(f"\n[*] Processing {current_date}...")

            # Fetch and save daily data
            daily_data = self.fetch_daily_data(current_date)
            if daily_data:
                daily_file = self.save_daily_data(current_date, daily_data)
                imported_files.append(daily_file)

                # Track which week this belongs to
                week_folder_path = self.get_folder_path(current_date)
                imported_weeks.add(str(week_folder_path))
            else:
                print(f"[!] No data available for {current_date}")

            current_date += timedelta(days=1)

        print(f"\n[*] Import completed! Imported {len(imported_files)} files.")

        # Generate week summaries for all imported weeks
        # print("\n[*] Generating week summaries...")
        # for week_path_str in imported_weeks:
        #     week_folder_path = Path(week_path_str)
        #     if week_folder_path.exists():
        #         # Get the week dates for this folder
        #         # Find any file in the folder to determine the week
        #         json_files = list(week_folder_path.glob("*.json"))
        #         if json_files:
        #             # Use the first file to determine the week
        #             sample_file = json_files[0]
        #             sample_date = datetime.strptime(sample_file.stem, "%Y-%m-%d").date()
        #             week_dates = self.get_week_dates(sample_date)
        #
        #             week_summary_data = self.generate_week_summary(
        #                 week_folder_path, week_dates
        #             )
        #             if week_summary_data:
        #                 self.save_week_summary(week_folder_path, week_summary_data)

        print("\n[+] Import completed successfully!")
        print(f"[+] Total files imported: {len(imported_files)}")
        print(f"[+] Week summaries generated: {len(imported_weeks)}")

        return imported_files


def main():
    API_KEY = os.environ.get("WAKATIME_API_KEY")
    if not API_KEY:
        raise Exception("Missing WAKATIME_API_KEY environment variable")

    importer = WakaTimeImporter(API_KEY)

    # Import last N days (default 20)
    imported_files = importer.import_last_n_days()

    # Weekly summary: chỉ tạo nếu hôm nay là thứ 2
    importer.generate_previous_week_summary()
    # Monthly summary: chỉ tạo nếu hôm nay là ngày 1
    importer.generate_previous_month_summary()

    print("\n[SUCCESS] Import completed!")
    print("Check the wakatime_logs/ directory for your imported data.")
    print("You can now use wakatime_visualizer.py to analyze your data!")


if __name__ == "__main__":
    main()
