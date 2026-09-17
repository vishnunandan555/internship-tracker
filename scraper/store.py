"""Load/save data/jobs.json and diff new scrape results against it.

jobs.json layout:
{
  "updated_at": "2026-07-09T12:00:00Z",
  "jobs": {
    "<uid>": {
      "company": ..., "external_id": ..., "title": ..., "url": ..., "locations": [...],
      "first_seen": "2026-07-09", "last_seen": "2026-07-09", "active": true
    }
  }
}

Jobs are never deleted; when a posting disappears from a successful scrape it is
flagged active=false (so first_seen survives a posting flapping on/off).
If a company's scraper FAILED this run, its existing jobs are left untouched.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jobs.json")
_TMP_PATH = DATA_PATH + ".tmp"


def _slugify(name: str) -> str:
    """Normalize company name to kebab-case slug matching Job.uid conventions."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load() -> dict:
    """Load jobs.json, returning a safe default if missing or corrupt."""
    if not os.path.exists(DATA_PATH):
        return {"updated_at": None, "jobs": {}}
    try:
        with open(DATA_PATH, encoding="utf-8") as fh:
            state = json.load(fh)
        if not isinstance(state, dict) or not isinstance(state.get("jobs"), dict):
            raise ValueError("Root state or 'jobs' key is not a dict")
        return state
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        print(f"[WARN] jobs.json corrupt ({exc}); starting fresh.", file=sys.stderr)
        corrupt_path = f"{DATA_PATH}.corrupt.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        try:
            os.replace(DATA_PATH, corrupt_path)
            print(f"[INFO] Backup saved to {corrupt_path}", file=sys.stderr)
        except OSError:
            pass
        return {"updated_at": None, "jobs": {}}


def save(state: dict) -> None:
    """Atomically persist state to jobs.json via a tmp-file + os.replace."""
    state["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(_TMP_PATH, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(_TMP_PATH, DATA_PATH)  # atomic on POSIX


def merge(state: dict, scraped_jobs: list, succeeded_companies: set) -> tuple:
    """Merge scraped Job objects into state.

    scraped_jobs: list[Job] from every company whose fetch SUCCEEDED.
    succeeded_companies: set of company display names that fetched without error.
    Returns (added, closed, reopened) lists of job dicts for reporting.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    jobs = state["jobs"]
    seen_uids: set = set()
    added, closed, reopened = [], [], []

    # Build slug set from succeeded company display names and jobs scraped this run.
    succeeded_slugs = {_slugify(n) for n in succeeded_companies}
    scraped_slugs = {job.uid.split(":", 1)[0] for job in scraped_jobs}

    for job in scraped_jobs:
        uid = job.uid
        seen_uids.add(uid)
        if uid in jobs:
            entry = jobs[uid]
            if not entry.get("active", True):
                entry["active"] = True
                reopened.append(entry)
            # Workday's relative "30+ Days Ago" degrades to posted=None once a
            # posting ages past 30 days — keep the date we captured earlier.
            known_posted = entry.get("posted")
            entry.update(job.to_dict())
            if not entry.get("posted") and known_posted:
                entry["posted"] = known_posted
            entry["last_seen"] = today
        else:
            entry = job.to_dict()
            entry["first_seen"] = today
            entry["last_seen"] = today
            entry["active"] = True
            jobs[uid] = entry
            added.append(entry)

    def _matches_succeeded(uid_slug: str, entry_company: str) -> bool:
        if entry_company in succeeded_companies:
            return True
        if uid_slug in scraped_slugs:
            return True
        entry_slug = _slugify(entry_company)
        for s_slug in succeeded_slugs:
            if uid_slug == s_slug or entry_slug == s_slug:
                return True
            # Handle rename variations with word boundaries (e.g. google vs google-llc)
            if s_slug.startswith(uid_slug + "-") or uid_slug.startswith(s_slug + "-"):
                return True
            if entry_slug and (s_slug.startswith(entry_slug + "-") or entry_slug.startswith(s_slug + "-")):
                return True
        return False

    # Close jobs only for companies that scraped successfully this run
    for uid, entry in list(jobs.items()):
        if uid in seen_uids or not entry.get("active", True):
            continue
        uid_slug = uid.split(":", 1)[0]
        entry_company = entry.get("company", "")

        if _matches_succeeded(uid_slug, entry_company):
            entry["active"] = False
            entry["closed"] = today
            closed.append(entry)

    return added, closed, reopened

