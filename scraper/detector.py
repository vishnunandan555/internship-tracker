"""Smart ATS Auto-Detector.

Given a careers page URL or company domain, analyzes redirects, HTML content,
and embedded script tags to identify the underlying Applicant Tracking System (ATS).
"""
import argparse
import re
import sys
from urllib.parse import urlparse

import requests

from .adapters import ashby, greenhouse, lever, smartrecruiters
from .http import USER_AGENT, request_text
from .models import Job


def detect_ats(url: str):
    """Analyze a URL and return a dict with detected ATS type, token/subdomain, and handler."""
    if not url.startswith("http"):
        url = "https://" + url

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    try:
        resp = session.get(url, allow_redirects=True, timeout=12)
        final_url = resp.url
        html = resp.text
    except Exception as e:
        return {"error": f"Failed to fetch {url}: {e}"}

    parsed = urlparse(final_url)
    domain = parsed.netloc.lower()

    # 1. Greenhouse
    gh_match = re.search(r"boards\.greenhouse\.io/(?:embed/job_board\?for=)?([a-zA-Z0-9_\-]+)", final_url + " " + html)
    if gh_match:
        token = gh_match.group(1)
        return {
            "ats": "Greenhouse",
            "token": token,
            "fetch": lambda cfg: greenhouse.fetch({"name": cfg.get("name", token), "token": token}),
        }

    # 2. Lever
    lever_match = re.search(r"jobs\.lever\.co/([a-zA-Z0-9_\-]+)", final_url + " " + html)
    if lever_match:
        token = lever_match.group(1)
        return {
            "ats": "Lever",
            "token": token,
            "fetch": lambda cfg: lever.fetch({"name": cfg.get("name", token), "site": token}),
        }

    # 3. SmartRecruiters
    sr_match = re.search(r"(?:careers|jobs)?\.smartrecruiters\.com/([a-zA-Z0-9_\-]+)", final_url + " " + html)
    if sr_match:
        token = sr_match.group(1)
        return {
            "ats": "SmartRecruiters",
            "token": token,
            "fetch": lambda cfg: smartrecruiters.fetch({"name": cfg.get("name", token), "company": token}),
        }

    # 4. Ashby
    ashby_match = re.search(r"jobs\.ashbyhq\.com/([a-zA-Z0-9_\-]+)", final_url + " " + html)
    if ashby_match:
        token = ashby_match.group(1)
        return {
            "ats": "Ashby",
            "token": token,
            "fetch": lambda cfg: ashby.fetch({"name": cfg.get("name", token), "org": token}),
        }

    # 5. Workday
    wd_match = re.search(r"([a-zA-Z0-9_\-]+)\.(?:wd\d+|myworkdayjobs)\.com/(?:[a-zA-Z\-]+/)?([a-zA-Z0-9_\-]+)", final_url + " " + html)
    if wd_match:
        tenant, site = wd_match.group(1), wd_match.group(2)
        return {
            "ats": "Workday",
            "host": f"{tenant}.myworkdayjobs.com",
            "site": site,
            "note": "Workday detected. Requires custom host & site configuration.",
        }

    # 6. Oracle HCM Cloud
    if "oraclecloud.com" in html or "oraclecloud.com" in final_url:
        return {
            "ats": "Oracle HCM Cloud",
            "note": "Oracle HCM instance detected.",
        }

    # 7. Eightfold AI
    if "eightfold.ai" in html or "eightfold.ai" in final_url:
        return {
            "ats": "Eightfold AI",
            "note": "Eightfold Career Experience detected.",
        }

    return {"ats": "Unknown / Custom Portal", "final_url": final_url}


def main():
    parser = argparse.ArgumentParser(description="Detect ATS and test fetching jobs from any career page URL.")
    parser.add_argument("url", help="Careers portal URL (e.g., https://jobs.lever.co/meesho or company careers URL)")
    parser.add_argument("--scrape", action="store_true", help="Attempt to scrape internships if supported ATS is detected")
    args = parser.parse_args()

    print(f"Detecting ATS for: {args.url}")
    result = detect_ats(args.url)
    ats = result.get("ats", "Unknown")
    print(f"Detected ATS: {ats}")

    if "token" in result:
        print(f"Identifier / Token: {result['token']}")

    if args.scrape and "fetch" in result:
        print("\nAttempting test fetch...")
        jobs = result["fetch"]({"name": "TestCompany"})
        interns = [j for j in jobs if j.looks_like_internship()]
        print(f"Total Postings: {len(jobs)} | Internships: {len(interns)}")
        for j in interns[:5]:
            print(f"  • {j.title} ({', '.join(j.locations)}) -> {j.url}")
    elif "note" in result:
        print(f"Note: {result['note']}")


if __name__ == "__main__":
    main()
