"""High-speed concurrent orchestrator for the India Tech Internships Tracker.

Usage:
    python -m scraper.main                     # Scrape all 40 companies concurrently (8 threads)
    python -m scraper.main -c qualcomm         # Scrape a single company
    python -m scraper.main -c "amd,phonepe"    # Scrape specific companies
    python -m scraper.main --dry-run           # Preview listings without writing to disk
    python -m scraper.main -k "hardware"       # Filter for hardware/specific roles
    python -m scraper.main --list              # List all configured & unsupported companies
"""
import argparse
import concurrent.futures
import json
import os
import shutil
import sys
import time

from . import display, store
from .categories import categorize
from .companies import COMPANIES, UNSUPPORTED
from .regions import get_city_tag, is_india_job
from .render_readme import render

HEALTH_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "health.json")
DOCS_JOBS_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "jobs.json")


def _scrape_single_company(cfg, keyword=None):
    """Worker function executed inside ThreadPoolExecutor for a single company."""
    name = cfg["name"]
    start_t = time.perf_counter()
    try:
        fetched = cfg["fetch"](cfg)
        interns = [j for j in fetched if j.looks_like_internship() and j.url]

        # Optional keyword filter (e.g. "hardware", "machine learning", "frontend")
        if keyword:
            kw = keyword.lower()
            interns = [j for j in interns if kw in j.title.lower()]

        for j in interns:
            j.category = categorize(j.title)
        in_scope = [j for j in interns if j.category]
        in_india = [j for j in in_scope if is_india_job(j.locations)]
        for j in in_india:
            j.city_tag = get_city_tag(j.locations)

        duration = time.perf_counter() - start_t
        return (name, in_india, len(fetched), len(interns), duration, None)
    except Exception as err:
        duration = time.perf_counter() - start_t
        return (name, [], 0, 0, duration, err)


def run(only_companies=None, keyword=None, dry_run=False, workers=8):
    """Run concurrent scraping across target companies."""
    # Filter target companies
    if only_companies:
        norm_targets = {c.strip().lower() for c in only_companies}
        targets = [c for c in COMPANIES if c["name"].lower() in norm_targets]
        if not targets:
            print(display.red(f"Error: No configured company matched {only_companies}."))
            print(display.dim("Use --list to see all supported company names."))
            return 1
    else:
        targets = COMPANIES

    print(display.bold(f"\n🚀 Launching scraper for {len(targets)} companies ({workers} worker threads)..."))
    if dry_run:
        print(display.yellow("⚠️  Running in DRY RUN mode: files will NOT be updated.\n"))
    else:
        print()

    all_jobs, succeeded, failed = [], set(), {}
    total_start_t = time.perf_counter()

    # Execute scrapers concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(workers, len(targets))) as executor:
        futures = {executor.submit(_scrape_single_company, cfg, keyword): cfg["name"] for cfg in targets}

        for future in concurrent.futures.as_completed(futures):
            name, in_india, n_fetched, n_interns, duration, err = future.result()
            if err is None:
                succeeded.add(name)
                all_jobs.extend(in_india)
                print(display.status_ok(name, duration, n_fetched, n_interns, len(in_india)))
            else:
                failed[name] = str(err)
                print(display.status_fail(name, duration, err))

    total_duration = time.perf_counter() - total_start_t

    if not succeeded:
        print(display.red("\nEvery attempted scraper failed — aborting without touching state."))
        return 1

    # In dry-run mode, display stats and exit without modifying database
    if dry_run:
        display.print_dashboard(
            total_duration=total_duration,
            succeeded=succeeded,
            failed=failed,
            added=[],
            closed=[],
            reopened=[],
            all_india_jobs=all_jobs,
            is_dry_run=True,
        )
        gh_output = os.environ.get("GITHUB_OUTPUT")
        if gh_output:
            with open(gh_output, "a") as fh:
                fh.write(f"added=0\nclosed=0\nfailed={len(failed)}\n")
        gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if gh_summary:
            with open(gh_summary, "a") as fh:
                fh.write("### ⚠️ Dry Run Completed (No Database Changes)\n\n")
                fh.write(f"- **Total Time:** `{total_duration:.1f}s`\n")
                fh.write(f"- **Companies Succeeded:** `{len(succeeded)}`\n")
                fh.write(f"- **Active India Postings Found:** `{len(all_jobs)}`\n\n")
        return 0

    # Merge into database and diff
    state = store.load()
    added, closed, reopened = store.merge(state, all_jobs, succeeded)
    store.save(state)
    render(state)

    # Sync a copy directly into docs/ so GitHub Pages loads without CORS or CDN latency
    try:
        os.makedirs(os.path.dirname(DOCS_JOBS_PATH), exist_ok=True)
        shutil.copyfile(store.DATA_PATH, DOCS_JOBS_PATH)
    except Exception as err:
        print(display.yellow(f"warning: could not sync docs/jobs.json: {err}"))

    # Record health
    os.makedirs(os.path.dirname(HEALTH_PATH), exist_ok=True)
    with open(HEALTH_PATH, "w") as fh:
        json.dump({"succeeded": sorted(succeeded), "failed": failed},
                  fh, indent=2, sort_keys=True)
        fh.write("\n")

    # Display full dashboard summary
    display.print_dashboard(
        total_duration=total_duration,
        succeeded=succeeded,
        failed=failed,
        added=added,
        closed=closed,
        reopened=reopened,
        all_india_jobs=all_jobs,
        is_dry_run=False,
    )

    # Surface the counts to GitHub Actions if running in CI
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a") as fh:
            fh.write(f"added={len(added)}\nclosed={len(closed)}\nfailed={len(failed)}\n")

    # Render a rich dashboard inside GitHub Actions Job Summary
    gh_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if gh_summary:
        with open(gh_summary, "a") as fh:
            fh.write("### 🚀 India Tech Internships Scrape Summary\n\n")
            fh.write(f"- **Runtime:** `{total_duration:.1f}s` (parallel execution)\n")
            fh.write(f"- **Companies Succeeded:** `{len(succeeded)}` | **Failed:** `{len(failed)}`\n")
            fh.write(f"- **Active India Internships:** `{len(all_jobs)}`\n")
            fh.write(f"- **New Postings Added:** `{len(added)}` | **Closed:** `{len(closed)}`\n\n")

            if added:
                fh.write("#### 🆕 New Internships Discovered\n\n")
                fh.write("| Company | Role | Hub | Category |\n|---|---|---|---|\n")
                for j in added:
                    loc = j.get("city_tag") or "India"
                    fh.write(f"| **{j['company']}** | [{j['title']}]({j['url']}) | {loc} | `{j.get('category', 'Tech')}` |\n")
                fh.write("\n")

            if failed:
                fh.write("#### ⚠️ Scraper Diagnostics\n\n")
                fh.write("| Company | Error Message |\n|---|---|\n")
                for c, err in sorted(failed.items()):
                    short_err = str(err).split("\n")[0][:80]
                    fh.write(f"| **{c}** | `{short_err}` |\n")
                fh.write("\n")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="High-speed concurrent internship scraper for India engineering roles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("targets", nargs="*", help="Optional company name(s) to scrape (e.g. Google Qualcomm)")
    parser.add_argument("-c", "--company", action="append", help="Company name to scrape (can be repeated or comma-separated)")
    parser.add_argument("-k", "--keyword", help="Custom keyword to filter internship titles (e.g. 'hardware', '2027')")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Preview scraped listings without modifying data/ or README")
    parser.add_argument("-s", "--search", help="Universal search for any company/keyword using Google Jobs/SERP API")
    parser.add_argument("-w", "--workers", type=int, default=8, help="Number of concurrent worker threads (default: 8)")
    parser.add_argument("-l", "--list", action="store_true", help="List all configured and unsupported companies")

    args = parser.parse_args()

    if args.search:
        from .adapters import serp_jobs
        print(display.bold(f"\n🔍 Querying Universal Job Search for: '{args.search}'..."))
        try:
            jobs = serp_jobs.fetch({"name": args.search, "query": args.search})
            print(display.green(f"Found {len(jobs)} postings:"))
            for j in jobs:
                loc = ", ".join(j.locations)
                print(f"  • {display.bold(j.company)} — {j.title} {display.cyan(loc)}")
                print(f"    {display.dim(j.url)}")
        except Exception as e:
            print(display.red(f"Error querying search API: {e}"))
            print(display.dim("Note: Requires SERP_API_KEY or RAPIDAPI_KEY set in environment."))
        return 0

    if args.list:
        print(display.bold(f"\nConfigured Scrapers ({len(COMPANIES)} companies):"))
        for c in sorted(COMPANIES, key=lambda x: x["name"]):
            print(f"  • {display.bold(c['name']):<24} (adapter: {c['fetch'].__module__.split('.')[-1]})")

        print(display.bold(f"\nDocumented Unsupported Companies ({len(UNSUPPORTED)} companies):"))
        for name, reason in sorted(UNSUPPORTED.items()):
            print(f"  × {display.bold(name):<24} {display.dim(reason)}")
        print()
        return 0

    # Combine positional args and --company flags
    selected = []
    if args.targets:
        selected.extend(args.targets)
    if args.company:
        for c in args.company:
            selected.extend([part.strip() for part in c.split(",") if part.strip()])

    return run(
        only_companies=set(selected) if selected else None,
        keyword=args.keyword,
        dry_run=args.dry_run,
        workers=args.workers,
    )


if __name__ == "__main__":
    sys.exit(main())
