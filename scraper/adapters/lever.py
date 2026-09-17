"""Lever job board adapter.

Endpoint: https://api.lever.co/v0/postings/{site}?mode=json
"""
from ..http import request_json
from ..models import Job, as_date, is_internship

API = "https://api.lever.co/v0/postings/{site}?mode=json"


def fetch(cfg):
    site = cfg["site"]
    url = API.format(site=site)
    postings = request_json("GET", url)
    jobs = []
    for p in postings:
        pid = str(p.get("id", ""))
        if not pid:
            continue
        title = p.get("text", "")
        cats = p.get("categories") or {}
        location = cats.get("location") or ""
        commitment = (cats.get("commitment") or "").strip()
        workplace = p.get("workplaceType") or ""
        
        locations = []
        if location:
            locations.append(location)
        if workplace and workplace.lower() == "remote" and "remote" not in location.lower():
            locations.append("Remote")

        is_intern = is_internship(title) or is_internship(commitment)
        created_at = p.get("createdAt")

        jobs.append(Job(
            company=cfg["name"],
            external_id=pid,
            title=title,
            url=p.get("hostedUrl") or p.get("applyUrl") or "",
            locations=locations,
            is_intern=is_intern,
            posted=as_date(created_at),
        ))
    return jobs
