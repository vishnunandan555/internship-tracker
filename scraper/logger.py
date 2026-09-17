"""Dual-tier logging system for scraper runs.

Outputs:
1. logs/scrape_full.log    - Complete technical log with per-company events, timings, and error traces.
2. logs/scrape_summary.log - Minimal executive summary with stats, added jobs, and health overview.
3. logs/history.log        - Append-only 1-line log tracking daily execution history over time.
"""
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Set

ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(REPO_ROOT, "logs")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from strings."""
    return ANSI_ESCAPE_RE.sub("", text)


class ScrapeLogger:
    def __init__(self):
        self.full_lines: List[str] = []
        self.start_time = datetime.now(timezone.utc)
        self.start_str = self.start_time.strftime("%Y-%m-%d %H:%M:%S UTC")

    def log(self, message: str, level: str = "INFO"):
        """Record a line in the full log buffer with a timestamp, sanitizing tracebacks."""
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        clean_msg = strip_ansi(message)
        # Redact any accidental tokens/keys in query params
        clean_msg = re.sub(r"(key|token|secret|password)=([^\s&]+)", r"\1=***REDACTED***", clean_msg, flags=re.IGNORECASE)
        lines = clean_msg.splitlines()
        if len(lines) > 3:
            clean_msg = f"{lines[0]} ... [truncated {len(lines) - 1} traceback lines]"
        self.full_lines.append(f"[{ts}] [{level:<5}] {clean_msg}")

    def save(self, total_duration: float, succeeded: Set[str], failed: Dict[str, str],
             added: List[dict], closed: List[dict], reopened: List[dict],
             all_india_jobs: List[dict]):
        """Write all log files to the logs/ directory."""
        os.makedirs(LOGS_DIR, exist_ok=True)
        end_time = datetime.now(timezone.utc)
        end_str = end_time.strftime("%Y-%m-%d %H:%M:%S UTC")

        # 1. logs/scrape_full.log
        full_path = os.path.join(LOGS_DIR, "scrape_full.log")
        header = [
            "=" * 72,
            f"INDIA TECH INTERNSHIPS TRACKER — DETAILED SCRAPE LOG",
            f"Started:  {self.start_str}",
            f"Finished: {end_str} ({total_duration:.1f}s)",
            f"Result:   {len(succeeded)} succeeded, {len(failed)} failed, {len(all_india_jobs)} active India listings",
            "=" * 72,
            "",
        ]
        with open(full_path, "w", encoding="utf-8") as fh:
            fh.writelines(line + "\n" for line in header)
            fh.writelines(line + "\n" for line in self.full_lines)

        # 2. logs/scrape_summary.log (Minimal, main info only)
        summary_path = os.path.join(LOGS_DIR, "scrape_summary.log")
        summary_lines = [
            "=" * 72,
            f"SCRAPE RUN SUMMARY — {self.start_str}",
            "=" * 72,
            f"Runtime:            {total_duration:.1f} seconds",
            f"Companies Scraped:  {len(succeeded) + len(failed)} total",
            f"  - Succeeded:      {len(succeeded)}",
            f"  - Failed:         {len(failed)}",
            f"Active India Roles: {len(all_india_jobs)}",
            f"Changes Detected:",
            f"  - New Additions:  +{len(added)}",
            f"  - Closed Roles:   -{len(closed)}",
            f"  - Reopened Roles: ~{len(reopened)}",
            "-" * 72,
        ]

        if added:
            summary_lines.append("\n[NEW INTERNSHIPS ADDED]")
            for j in added:
                comp = j.get("company", "Unknown")
                title = j.get("title", "Unknown")
                loc = j.get("city_tag") or "India"
                cat = j.get("category", "Software")
                url = j.get("url", "")
                summary_lines.append(f"  + {comp} — {title} ({loc}) [{cat}]")
                summary_lines.append(f"    Apply: {url}")

        if closed:
            summary_lines.append("\n[INTERNSHIPS CLOSED]")
            for j in closed:
                comp = j.get("company", "Unknown")
                title = j.get("title", "Unknown")
                loc = j.get("city_tag") or "India"
                summary_lines.append(f"  - {comp} — {title} ({loc})")

        if failed:
            summary_lines.append("\n[FAILED SCRAPERS]")
            for name, err in sorted(failed.items()):
                short_err = str(err).split("\n")[0][:80]
                summary_lines.append(f"  × {name}: {short_err}")

        summary_lines.append("\n" + "=" * 72 + "\n")

        with open(summary_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(summary_lines))

        # 3. logs/history.log (Append-only daily history)
        history_path = os.path.join(LOGS_DIR, "history.log")
        history_entry = (
            f"[{end_str}] "
            f"OK: {len(succeeded)}/{len(succeeded) + len(failed)} | "
            f"Active: {len(all_india_jobs)} | "
            f"+{len(added)} new, -{len(closed)} closed | "
            f"Runtime: {total_duration:.1f}s\n"
        )
        with open(history_path, "a", encoding="utf-8") as fh:
            fh.write(history_entry)
