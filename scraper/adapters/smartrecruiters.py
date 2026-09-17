"""SmartRecruiters job board adapter (Swiggy, ServiceNow, etc.).

API: https://api.smartrecruiters.com/v1/companies/{company}/postings
"""
import time

from ..http import request_json
from ..models import Job, as_date, is_internship

API = "https://api.smartrecruiters.com/v1/companies/{company}/postings"
JOB_URL = "https://jobs.smartrecruiters.com/{company}/{id}"
PAGE = 100
MAX_PAGES = 15


def fetch(cfg):
    company = cfg["company"]
    url = API.format(company=company)
    jobs, offset = [], 0

    for _ in range(MAX_PAGES):
        data = request_json("GET", url, params={"limit": PAGE, "offset": offset})
        content = data.get("content", [])
        for item in content:
            iid = str(item.get("id", ""))
            if not iid:
                continue
            title = item.get("name", "")
            loc_obj = item.get("location") or {}
            full_loc = loc_obj.get("fullLocation") or ""
            city = loc_obj.get("city") or ""
            region = loc_obj.get("region") or ""
            country = loc_obj.get("country") or ""

            locations = []
            if full_loc:
                locations.append(full_loc)
            elif city or country:
                locations.append(f"{city}, {region}, {country}".strip(", "))

            if loc_obj.get("remote"):
                locations.append("Remote")

            type_of_emp = (item.get("typeOfEmployment") or {}).get("label") or ""
            exp_level = (item.get("experienceLevel") or {}).get("label") or ""

            is_intern = (
                is_internship(title)
                or is_internship(type_of_emp)
                or is_internship(exp_level)
            )

            released_date = item.get("releasedDate")

            jobs.append(Job(
                company=cfg["name"],
                external_id=iid,
                title=title,
                url=JOB_URL.format(company=company, id=iid),
                locations=locations,
                is_intern=is_intern,
                posted=as_date(released_date),
            ))

        offset += PAGE
        total = data.get("totalFound", 0)
        if not content or offset >= total:
            break
        time.sleep(0.5)

    return jobs
