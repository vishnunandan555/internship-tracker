# Roadmap

Realistic improvements planned for the scraper.

---

## ✅ Already Shipped / In Progress

- [x] `--dry-run` flag — show what would be scraped without writing to the DB
- [x] `--company <name>` flag — re-scrape a single company on demand
- [x] GitHub Actions: surface new listings in the workflow step summary
- [ ] Progress bar while scraping (replace per-company lines with a live `tqdm` or `rich` progress bar)
- [ ] Export snapshot to CSV (`--export csv`)
- [ ] Skip companies with 0 India listings from the final summary output by default; `--verbose` to show all
- [ ] GitHub Actions: post new listings as a comment on the workflow run summary instead of just the step summary

---

## 🔥 Quick Wins (High Impact, Low Effort)

### 1. Atomic File Writes in `store.py`
**Why:** `store.save()` writes directly to `jobs.json`. If the process crashes or is killed mid-write, the file is left corrupt and every subsequent run will fail to load state — silently losing historical data.  
**How:** Write to a `.tmp` file first, then call `os.replace(tmp_path, DATA_PATH)`. This is an atomic operation on all POSIX systems and takes 3 lines of code.

```python
# store.py
tmp = DATA_PATH + ".tmp"
with open(tmp, "w") as fh:
    json.dump(state, fh, indent=2, sort_keys=True)
    fh.write("\n")
os.replace(tmp, DATA_PATH)
```

---

### 2. Retry Logic & Exponential Backoff in `http.py`
**Why:** Several companies (Oracle 40s, Morgan Stanley 59s) show high latency consistent with rate-limiting. A single transient timeout marks the whole company as `[FAIL]` and leaves its existing jobs untouched — meaning a brief network hiccup silently prevents closures from being detected.  
**How:** Add a retry decorator using `tenacity` (already a common dep) or a manual loop with jitter:

```python
# http.py — wrap request_text with up to 3 retries, exponential backoff
for attempt in range(3):
    try:
        return session.get(url, timeout=15).text
    except requests.RequestException:
        if attempt == 2:
            raise
        time.sleep(2 ** attempt + random.uniform(0, 1))
```

---

### 3. New-Grad / Fresher Detection in `models.py`
**Why:** The current `INTERN_RE` regex only matches `intern`, `internship`, and `co-op`. Titles like `"Graduate Hire"`, `"New Grad"`, `"Fresher"`, `"Associate Engineer – 2027"`, or `"Campus Hire"` are silently dropped. GitHub (78 postings → 0 interns), Swiggy (98 → 0), and InMobi (61 → 0) are likely victims of this.  
**How:** Add a secondary regex and a `looks_like_new_grad()` method, or extend `INTERN_RE`:

```python
NEWGRAD_RE = re.compile(
    r"(?:new[\s\-]?grad|fresher|campus|graduate\s+hire|entry[\s\-]?level"
    r"|associate\s+engineer|20(?:26|27)\s+grad)",
    re.IGNORECASE,
)

def looks_like_internship(self) -> bool:
    if self.is_intern is not None:
        return self.is_intern
    return bool(INTERN_RE.search(self.title) or NEWGRAD_RE.search(self.title))
```

---

### 4. Configurable Notifications on New Listings
**Why:** The scraper already detects `added` listings — but discovery is passive. You only find out by re-running the CLI or checking the README. A push notification makes the signal actionable.  
**How:** Add an optional `--notify` flag. On new listings, POST to a Telegram bot (single `requests.post` call, needs only `BOT_TOKEN` + `CHAT_ID` env vars), or fall back to `smtplib` email. Wire it into `main.py` after `store.merge()`.

---

## ⚙️ Medium-Effort Improvements

### 5. Expose Truncated Results (999-posting Sentinel)
**Why:** Oracle and JPMorgan both return exactly **999 postings** — this is almost certainly an API/pagination cap, not the real count. The adapter silently stops paginating and may miss internship listings that appear on later pages. This is a silent correctness bug.  
**How:** Each adapter should return a `(jobs, truncated: bool)` tuple or set a `truncated` field on the result. `main.py` should print a `⚠️ TRUNCATED` warning next to companies that hit the cap and log it to `health.json`. Separately, fix the pagination logic in `oracle_hcm.py` and `workday.py` to paginate until exhausted.

---

### 6. ATS Health Tracking — Consecutive Failure Detection
**Why:** `health.json` only records pass/fail for the last run. If an adapter silently breaks (e.g., the ATS changed its API schema), it will keep "succeeding" with 0 results, or failing, for weeks before anyone notices.  
**How:** Persist a `consecutive_failures` counter per company in `health.json`. Increment on fail, reset on success. In `main.py`, emit a `⚠️ STALE` warning if any company has ≥3 consecutive failures or if a large company (>50 historical postings) suddenly returns 0.

```json
// health.json (proposed schema addition)
{
  "companies": {
    "Oracle": { "consecutive_failures": 0, "last_success": "2026-09-17", "last_postings": 999 }
  }
}
```

---

### 7. `--list` Shows India History
**Why:** `--list` shows adapter names but not which companies have ever yielded India results. When debugging or onboarding new companies, knowing that "Intel has returned India listings before but GitHub never has" is immediately useful.  
**How:** Load `jobs.json` in the `--list` handler, group by company, and annotate each entry with `✓ N India jobs (last seen YYYY-MM-DD)` or `✗ no India history`.

---

## 🏗️ Larger Architectural Changes

### 8. Async I/O: `asyncio` + `httpx` Instead of `ThreadPoolExecutor`
**Why:** The current thread pool blocks OS threads on network I/O. With 42 companies and `--workers 10`, at most 10 are truly concurrent. Slow scrapers (Amazon 28s, Oracle 40s, Microsoft 51s) block slots. `asyncio` with `httpx.AsyncClient` allows hundreds of concurrent requests without thread overhead — the 95s total runtime could likely drop to ~60s.  
**How:** Replace `ThreadPoolExecutor` in `main.py` with `asyncio.gather()`. Convert all adapters to `async def fetch(cfg)` using `await client.get(url)`. Use `httpx.AsyncClient` with a shared client and connection pool. This is the largest refactor but the gains compound with every new company added.

---

### 9. Incremental / Skip-Unchanged Scraping
**Why:** Every run re-fetches all 42 companies unconditionally. Most companies change infrequently — running the full scrape every 6 hours is wasteful and increases the chance of being rate-limited.  
**How:** Two approaches:
- **HTTP-level:** Send `If-None-Match` / `If-Modified-Since` headers where the ATS supports them; skip parsing on `304 Not Modified`.
- **App-level:** Track `last_changed` per company in `health.json`. If a company has had 0 changes in the last N runs, scrape it less frequently (e.g., once per day instead of every 6 hours).

---

### 10. Config-as-Data: Move `companies.py` to `companies.yaml`
**Why:** Adding a new company currently requires editing Python source, knowing which adapter to import, and understanding the config dict schema. This creates friction and makes the project hard for contributors to extend without understanding the codebase.  
**How:** Define companies in a `companies.yaml` file:

```yaml
- name: Google
  adapter: google
  # adapter-specific keys passed through as cfg
  client_id: "..."

- name: Greenhouse Company
  adapter: greenhouse
  token: "sometoken"
```

At startup, load the YAML and resolve the adapter string to a module via a registry dict (`{"greenhouse": greenhouse.fetch, ...}`). Adding a new company becomes a one-line YAML edit with zero Python knowledge required.
