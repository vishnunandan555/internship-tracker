"""Render README.md from data/jobs.json. The README is generated — never hand-edit."""
import os
from datetime import datetime, timedelta, timezone

README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
NEW_BADGE_DAYS = 7
IST = timezone(timedelta(hours=5, minutes=30))


def _to_ist_str(iso_utc: str) -> str:
    """Convert UTC ISO timestamp to formatted IST timestamp string."""
    try:
        dt = datetime.strptime(iso_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return dt.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception:
        return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")


HEADER = """\
# 🇮🇳 Software Engineering & Tech Internship Tracker — India

Auto-updated list of **open tech & software-engineering internships in India** —
AI/ML, Data, Full-Stack, Backend, Frontend, Mobile, QA/SDET, and Security roles — at
{n_companies} top tech companies, GCCs, and high-growth Indian unicorns. Scraped directly
from official careers APIs daily (at 05:30 AM IST) by GitHub Actions.

🌐 **Live Web Dashboard: [vishnunandan555.github.io/internship-tracker](https://vishnunandan555.github.io/internship-tracker/)** · 🛠️ **[GUIDE.md](GUIDE.md)** · 🚀 **[ROADMAP.md](ROADMAP.md)** · 📋 **[Scrape Logs](logs/)**

> 🕐 Last updated: **{updated}** · 📌 **{n_open}** open internships
> · 🆕 = added in the last {new_days} days

⭐ Star this repository to keep track of new openings — or watch *Activity* for commits titled “new internship(s)”.

"""

FOOTER = """
---

## ⚙️ How This Works

A high-speed concurrent [Python scraper](scraper/) runs in GitHub Actions daily at 05:30 AM IST:
1. Concurrently queries official careers APIs (Workday, Greenhouse, SmartRecruiters, Lever, Eightfold, Phenom, Oracle HCM, and custom REST APIs).
2. Filters for active internships, co-ops, and trainee engineering roles ([scraper/categories.py](scraper/categories.py)).
3. Strictly filters locations within India tech hubs (Bengaluru, Hyderabad, Pune, Delhi-NCR, Chennai, Mumbai, and Remote India) ([scraper/regions.py](scraper/regions.py)).
4. Diffs against [`data/jobs.json`](data/jobs.json) to track additions, closures, and re-openings.
5. Auto-updates this `README.md`, execution logs in [`logs/`](logs/), and the interactive web dashboard in `docs/`.

📖 **Looking for CLI usage, ATS auto-detection, architecture, or adding a company? Read the [Developer & System Guide (GUIDE.md)](GUIDE.md).**

Found an issue or want to request a company? Feel free to open an issue or pull request!
"""


def _slug(name):
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


def _md_escape(text):
    return text.replace("|", "\\|").strip()


def _fmt_locations(locations, limit=2):
    locs = [l for l in locations if l]
    if not locs:
        return "India"
    shown = "; ".join(_md_escape(l) for l in locs[:limit])
    extra = len(locs) - limit
    if extra > 0:
        shown += " *(+{} more)*".format(extra)
    return shown


def render(state):
    from .companies import COMPANIES, UNSUPPORTED
    tracked = [c["name"] for c in COMPANIES]
    jobs = [j for j in state["jobs"].values() if j.get("active", True)]
    updated = state.get("updated_at") or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=NEW_BADGE_DAYS)).strftime("%Y-%m-%d")

    by_company = {name: [] for name in tracked}
    for j in jobs:
        by_company.setdefault(j["company"], []).append(j)

    companies = sorted(by_company)
    out = [HEADER.format(
        n_companies=len(companies),
        updated=_to_ist_str(updated),
        n_open=len(jobs),
        new_days=NEW_BADGE_DAYS,
    )]

    # summary table with anchors
    out.append("| Company | Open Internships in India |\n|---|:---:|\n")
    for c in companies:
        n = len(by_company[c])
        label = "[{}](#{})".format(c, _slug(c)) if n else c
        out.append("| {} | {} |\n".format(label, f"**{n}**" if n else "—"))
    for name, why in sorted(UNSUPPORTED.items()):
        out.append("| {} | *{}* |\n".format(name, why))
    out.append("\n---\n\n")

    for c in companies:
        if not by_company[c]:
            continue
        rows = sorted(by_company[c],
                      key=lambda j: (j.get("posted") or j.get("first_seen", ""),
                                     j["title"]),
                      reverse=True)
        out.append("## {}\n\n".format(c))
        out.append("| Role | Category | Hub / Location | Posted | First seen |\n"
                   "|---|---|---|---|---|\n")
        for j in rows:
            is_new = (j.get("first_seen") or "") >= cutoff
            badge = " 🆕" if is_new else ""
            title = "[{}]({}){}".format(_md_escape(j["title"]), j["url"], badge)
            cat = j.get("category") or "Software"
            hub = j.get("city_tag") or _fmt_locations(j.get("locations", []))
            posted = j.get("posted") or "—"
            first_seen = j.get("first_seen") or "—"
            out.append("| {} | {} | {} | {} | {} |\n".format(
                title, cat, hub, posted, first_seen))
        out.append("\n")

    out.append(FOOTER)

    with open(README_PATH, "w") as fh:
        fh.write("".join(out))
