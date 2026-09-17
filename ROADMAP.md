# 🗺️ Project Roadmap & TODO Tracker

A living tracker of shipped features, active development items, and upcoming milestones for **InternTrack India**.

---

## 📊 Status Overview

| Phase | Focus Area | Status | Progress |
|---|---|:---:|:---:|
| **Phase 1** | Scraper Core & 55+ ATS Adapters | Complete | 100% |
| **Phase 2** | Live Web Dashboard & UI/UX | Complete | 100% |
| **Phase 3** | Technical SEO & Discoverability | Complete | 100% |
| **Phase 4** | Automated Community Alerts & Notifications | In Progress | 40% |
| **Phase 5** | Growth, Distribution & Launchpad Marketing | Next Up | 15% |
| **Phase 6** | Platform Scaling & New-Grad Expansion | Planned | 0% |

---

## ✅ Completed Milestones

- [x] **55+ Tier-1 Tech Company Adapters**: Official careers APIs scraped directly across FAANG, top GCCs, and high-growth Indian unicorns.
- [x] **High-Speed Concurrent Engine**: Thread-safe concurrent scraper (`ThreadPoolExecutor`, 8 workers) with exponential backoff and custom session reuse.
- [x] **Zero Ghost Jobs Policy**: Automated removal of expired or closed postings on every daily run.
- [x] **Daily Automated GitHub Actions Workflow**: Runs daily at 03:00 AM IST (21:30 UTC) with automatic commit and push.
- [x] **Dual-Tier Audit Logging**: Detailed JSON and human-readable text logs archived in `logs/` for every run.
- [x] **Interactive Web Dashboard**:
  - [x] Responsive dark/light theme with ambient glow styling.
  - [x] Card View and Compact Table View toggle.
  - [x] Instant client-side search across role, company, skills, and locations (`/` shortcut).
  - [x] Tech Hub filters (Bengaluru, Hyderabad, Pune, Delhi-NCR, Chennai, Mumbai, Remote).
  - [x] Role categorization (SDE, AI/ML, Data, Backend/Infra, Frontend, Mobile, QA, Security, Hardware).
  - [x] Local bookmarking ("Saved Roles") persisted in browser `localStorage`.
- [x] **Technical SEO & Discoverability**:
  - [x] High-intent title & meta descriptions for 2026/2027 batch tech internships.
  - [x] `docs/robots.txt` allowing full indexing.
  - [x] `docs/sitemap.xml` with automatic daily `<lastmod>` sync via `scraper/main.py`.
  - [x] Static Schema.org `WebSite` & `WebApplication` JSON-LD markup.
  - [x] Dynamic Schema.org `ItemList` & `JobPosting` structured data injection for Google for Jobs.
  - [x] Deep-link URL query synchronization (`?q=`, `?company=`, `?hub=`, `?cat=`, `?sort=`).
  - [x] Clean, high-resolution OpenGraph and Twitter preview card (`docs/og-image.png`).
- [x] **Growth & Marketing Playbook**: Comprehensive [SEO.md](SEO.md) covering keyword clusters, Reddit/LinkedIn copy, and distribution channels.

---

## 📌 Active TODOs (High Priority / Next Up)

### Automation & Alerts
- [ ] **Discord & Telegram Webhook Broadcaster**:
  - Create a script (`scripts/broadcast_alerts.py`) or CI step triggered when `added > 0`.
  - Send formatted rich embed cards to student Discord servers and Telegram channels.
- [ ] **Live CLI Progress Indicators**:
  - Replace scrolling stdout lines with an interactive terminal progress bar (`rich` or `tqdm`) for local developer runs.
- [ ] **CSV Export (`--export csv`)**:
  - Add CLI option to dump active listings to a CSV snapshot for Notion / Excel tracking.

### Community & Growth Execution
- [ ] **Google Search Console (GSC) Submission**:
  - Verify domain ownership and submit `sitemap.xml` for indexation.
- [ ] **Bing Webmaster Tools & IndexNow**:
  - Set up IndexNow key for instant re-indexing on daily sync.
- [ ] **GitHub Repository Optimization**:
  - [ ] Add all 15 target topics to GitHub repo settings.
  - [ ] Set `docs/og-image.png` as GitHub Social Preview in repo settings.
  - [ ] Submit PRs to high-traffic `awesome-*` lists (`awesome-india`, `awesome-internships`).
- [ ] **Community Launch**:
  - [ ] Post launch introduction on `r/developersIndia`.
  - [ ] Share tailored guide on `r/Btechtards` and `r/csMajors`.
  - [ ] Launch weekly "Monday Internship Radar" series on LinkedIn.

---

## ⚙️ Upcoming Feature Enhancements

- [ ] **Consecutive Failure Tracking**:
  - Track consecutive failure counts per company in `health.json` to flag permanently decommissioned career URLs.
- [ ] **New-Grad & Entry-Level Expansion (`--freshers`)**:
  - Add support for entry-level / new-grad full-time roles alongside internships.
- [ ] **Truncated Result Sentinel**:
  - Detect when API responses hit hard pagination limits (e.g. 999 postings) and flag potential overflow.
- [ ] **HTTP Cache Header Optimization**:
  - Utilize `If-Modified-Since` and `ETag` headers to skip unchanged company career portals and reduce network bandwidth.
- [ ] **Role Tenure & Duration Tracking**:
  - Display "Days Active" badge on postings to help students prioritize roles nearing closure.

---

## 🏗️ Architecture & Long-Term Vision

- [ ] **Async I/O Engine (`httpx` + `asyncio`)**:
  - Migrate from `concurrent.futures.ThreadPoolExecutor` to native asynchronous coroutines when tracking 100+ company portals.
- [ ] **Declarative Registry (`companies.yaml`)**:
  - Decouple company adapter metadata into a declarative YAML specification if external community contributions scale up.
- [ ] **Custom Domain Setup**:
  - Deploy to a dedicated custom domain (e.g., `interntrack.in` or `internships-india.dev`) with Cloudflare CDN caching.
