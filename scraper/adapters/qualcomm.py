"""Qualcomm PCSX / Eightfold careers API."""
from datetime import datetime, timezone
import time
import requests

from ..http import USER_AGENT, request_json
from ..models import Job

BASE_URL = "https://careers.qualcomm.com/careers"
API = "https://careers.qualcomm.com/api/pcsx/search"
JOB_URL = "https://careers.qualcomm.com/careers/job/{id}?domain=qualcomm.com"
PAGE_SIZE = 10
MAX_PAGES = 10


def fetch(cfg):
    domain = cfg.get("domain", "qualcomm.com")
    query = cfg.get("query", "intern")
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Referer": BASE_URL,
    })

    # Warm session cookies from base careers portal
    try:
        session.get(BASE_URL, timeout=15)
    except Exception:
        pass

    jobs, start = [], 0

    for _ in range(MAX_PAGES):
        params = {
            "domain": domain,
            "query": query,
            "start": start,
            "sort_by": "relevance",
        }
        data = request_json("GET", API, params=params, session=session)
        res_data = data.get("data") or {}
        positions = res_data.get("positions", [])
        total = res_data.get("count", 0)

        for p in positions:
            pid = str(p.get("id") or p.get("displayJobId") or "")
            title = p.get("name", "")
            locations = p.get("locations") or []
            if not locations and p.get("standardizedLocations"):
                locations = p.get("standardizedLocations")

            posted_date = None
            if p.get("postedTs"):
                try:
                    ts = float(p["postedTs"])
                    if ts > 1e11:  # milliseconds
                        ts /= 1000.0
                    posted_date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                except (ValueError, TypeError, OSError):
                    pass

            jobs.append(Job(
                company=cfg["name"],
                external_id=pid,
                title=title,
                url=JOB_URL.format(id=pid),
                locations=[str(loc) for loc in locations if loc],
                posted=posted_date,
            ))

        start += len(positions)
        if not positions or start >= total:
            break
        time.sleep(0.5)

    return jobs
