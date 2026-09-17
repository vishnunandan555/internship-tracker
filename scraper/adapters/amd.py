"""AMD careers (Jibe API).

GET https://careers.amd.com/api/jobs?keywords={kw}&page={page}
"""
import time

from ..http import request_json
from ..models import Job, as_date

API = "https://careers.amd.com/api/jobs"
JOB_URL = "https://careers.amd.com/careers-home/jobs/{slug}"
MAX_PAGES = 10


def fetch(cfg):
    query = cfg.get("query", "intern")
    jobs = []

    for page in range(1, MAX_PAGES + 1):
        params = {"keywords": query, "page": page}
        data = request_json("GET", API, params=params)
        raw_jobs = data.get("jobs", [])
        if not raw_jobs:
            break

        for item in raw_jobs:
            d = item.get("data", {})
            slug = d.get("slug") or d.get("req_id") or ""
            title = d.get("title", "")
            locations = []
            if d.get("short_location"):
                locations.append(d["short_location"])
            elif d.get("city") or d.get("country"):
                loc = ", ".join(x for x in (d.get("city"), d.get("state"), d.get("country")) if x)
                if loc:
                    locations.append(loc)
            ml_val = d.get("multipleLocations")
            if isinstance(ml_val, list):
                for ml in ml_val:
                    if isinstance(ml, str):
                        locations.append(ml)

            jobs.append(Job(
                company=cfg["name"],
                external_id=str(slug),
                title=title,
                url=JOB_URL.format(slug=slug),
                locations=locations or ["India"],
                posted=as_date(d.get("create_date") or d.get("posted_date")),
            ))

        total_pages = data.get("total_pages") or 1
        if page >= total_pages:
            break
        time.sleep(0.5)

    return jobs
