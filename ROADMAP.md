# Roadmap

Planned improvements and future features for the scraper.

---

## 🚀 High Priority / Next Up

- **Live Progress Bar**: Add an interactive terminal progress bar (`rich` or `tqdm`) during concurrent scraping instead of scrolling lines.
- **Discord / Telegram Notifications**: Dispatch webhook alerts on daily CI runs when new internships (`added > 0`) are discovered.
- **CSV Export (`--export csv`)**: Export current active listings to a CSV snapshot for Notion / Excel tracking.
- **`--list` Historical Stats**: Annotate `python -m scraper.main --list` with active posting counts and last-seen dates from `jobs.json`.

---

## ⚙️ Feature Enhancements

- **Consecutive Failure Tracking**: Record consecutive failure counters in `health.json` to identify permanently broken ATS portals.
- **New-Grad / Fresher Filter**: Optional CLI flag (`--freshers`) to capture campus graduate and entry-level engineering roles.
- **Truncated Result Sentinel**: Detect when companies hit API pagination caps (e.g. 999 postings) and warn about potential missed listings.
- **Incremental Scraping**: Use HTTP cache headers (`If-Modified-Since`) to avoid scraping unchanged career portals.

---

## 🏗️ Architecture (Long-Term)

- **Async I/O (`httpx` + `asyncio`)**: Transition from `ThreadPoolExecutor` to native async coroutines if scraping 100+ companies.
- **Config as Data (`companies.yaml`)**: Externalize company registry into declarative YAML if external contribution volume warrants it.
