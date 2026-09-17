"""Orchestrator: fetch every company, filter internships, apply India location filter, diff, render README.

Usage:
    python -m scraper.main             # scrape all companies
    python -m scraper.main Google Meta # scrape a subset (for debugging)

Exit code is non-zero only on total failure; individual company failures are
reported (and written to data/health.json) but don't fail the run.
"""
import json
import os
import shutil
import sys
import time
import traceback

from . import store
from .categories import categorize
from .companies import COMPANIES
from .regions import get_city_tag, is_india_job
from .render_readme import render

HEALTH_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "health.json")
DOCS_JOBS_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "jobs.json")


def run(only=None):
    all_jobs, succeeded, failed = [], set(), {}

    for cfg in COMPANIES:
        name = cfg["name"]
        if only and name not in only:
            continue
        try:
            fetched = cfg["fetch"](cfg)
            interns = [j for j in fetched if j.looks_like_internship() and j.url]
            for j in interns:
                j.category = categorize(j.title)
            in_scope = [j for j in interns if j.category]
            in_india = [j for j in in_scope if is_india_job(j.locations)]
            for j in in_india:
                j.city_tag = get_city_tag(j.locations)

            print("[ok]   {:<24} {:>4} postings, {:>3} internships, {:>3} in scope, {:>3} in India".format(
                name, len(fetched), len(interns), len(in_scope), len(in_india)))

            all_jobs.extend(in_india)
            succeeded.add(name)
        except Exception as err:  # noqa: BLE001 - isolate per-company failures
            failed[name] = str(err)
            print("[FAIL] {:<24} {}".format(name, err))
            traceback.print_exc()
        time.sleep(1)

    if not succeeded:
        print("every scraper failed — aborting without touching data")
        return 1

    state = store.load()
    added, closed, reopened = store.merge(state, all_jobs, succeeded)
    store.save(state)
    render(state)

    # Sync a copy directly into docs/ so GitHub Pages loads without CORS or CDN latency
    try:
        os.makedirs(os.path.dirname(DOCS_JOBS_PATH), exist_ok=True)
        shutil.copyfile(store.DATA_PATH, DOCS_JOBS_PATH)
    except Exception as err:
        print("warning: could not sync docs/jobs.json: {}".format(err))

    os.makedirs(os.path.dirname(HEALTH_PATH), exist_ok=True)
    with open(HEALTH_PATH, "w") as fh:
        json.dump({"succeeded": sorted(succeeded), "failed": failed},
                  fh, indent=2, sort_keys=True)
        fh.write("\n")

    print("\nadded={} closed={} reopened={} | scrapers ok={} failed={}".format(
        len(added), len(closed), len(reopened), len(succeeded), len(failed)))
    for j in added:
        print("  + {} — {} ({})".format(j["company"], j["title"], j.get("city_tag", "")))

    # surface the counts to the GitHub Actions step that writes the commit message
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as fh:
            fh.write("added={}\nclosed={}\nfailed={}\n".format(
                len(added), len(closed), len(failed)))
    return 0


if __name__ == "__main__":
    sys.exit(run(only=set(sys.argv[1:]) or None))
