# 🚀 Product Roadmap & Upcoming Features

This document tracks planned improvements, community-requested features, and future development milestones for the **India Tech Internships Tracker**.

---

## 📌 Progress Summary

- **Completed**: Concurrent ThreadPool scraper engine, CLI interface (`-c`, `-k`, `-d`, `-s`, `-l`), rich terminal dashboard, ATS auto-detector (`scraper/detector.py`), GitHub Actions pip caching, and `GITHUB_STEP_SUMMARY` reporting.
- **In Progress**: Real-time notifications and student application helper tools.

---

## 🔔 Milestone 1: Instant Real-Time Notifications

Never miss an opening when a company drops a posting at 2 AM.

- [ ] **Telegram Channel / Bot Integration**
  - Broadcast new listings instantly to a public Telegram channel.
  - Formatted message with Company, Role, Hub (BLR/HYD/Pune), and a 1-click apply button.
- [ ] **Discord Webhook Alerts**
  - Post rich Discord embeds into a `#job-alerts` channel for college and developer Discord servers.
  - Include role tags (`#software`, `#hardware`, `#aiml`).
- [ ] **RSS / Atom Feed (`docs/feed.xml`)**
  - Generate a standardized RSS feed on every scrape run so users can subscribe via Slack RSS, Feedly, or NetNewsWire.
- [ ] **WhatsApp Community Alerts** (via Twilio or WhatsApp Business Webhook).

---

## 🎯 Milestone 2: Smart Eligibility & Batch Classifier

Cut down noise by highlighting exactly which graduation year each role targets.

- [ ] **Graduation Year Extraction (2026 / 2027 / 2028)**
  - Parse job titles and descriptions with regex to extract target graduation years (e.g. Qualcomm's `Intern_2027_SW`).
  - Add a dedicated `Batch: 2027` badge on the web UI and in `README.md`.
- [ ] **Degree & Year Level Tagging**
  - Distinguish between **Pre-final Year (Summer 2026/2027)** vs **Final Year (6-month / Jan–June Co-op)** vs **Fresh Graduate Internships**.
  - Tag degree requirements (`B.Tech / B.E.`, `M.Tech / M.S.`, `Dual Degree`, `MCA`, `PhD`).
- [ ] **Pre-requisite / CGPA Flagging**
  - Flag postings with hard CGPA thresholds (e.g., "7.5+ CGPA required" or "No active backlogs").

---

## 💻 Milestone 3: Interactive Web Dashboard Superpowers

Transform the static web page (`docs/index.html`) into a student command center.

- [ ] **Personal "Applied / Starred" Tracker (Local Storage)**
  - Add a "⭐ Save" and "✅ Mark as Applied" button next to each job.
  - Persist state in browser `localStorage` — no login, database, or accounts required.
- [ ] **Application Deadline & Age Indicators**
  - Show how many hours/days ago the posting was detected (e.g., `⚡ Posted 4 hours ago`).
  - Urgency indicators for high-volume companies (Google/Microsoft) that close within 48–72 hours.
- [ ] **1-Click Share Card Generator**
  - Generate clean preview image / text cards for sharing openings on LinkedIn, X (Twitter), or WhatsApp groups.
- [ ] **PWA (Progressive Web App) Support**
  - Add web manifest and service worker so students can "Install" the tracker as a native app on Android/iOS.

---

## 🤝 Milestone 4: 1-Click Referral Link Generator

Getting an employee referral increases interview rates by 4x.

- [ ] **Smart LinkedIn Referral Search Button**
  - Add a "Find Referral" button on each listing that dynamically opens a pre-filtered LinkedIn search:
    `https://www.linkedin.com/search/results/people/?keywords={Company}+Software+Engineer+{City}`
  - Includes quick-copy cold-outreach message templates tailored to university students.
- [ ] **Alumni Connect Helper**
  - Allow users to enter their university name (e.g., `IIT Bombay`, `BITS Pilani`, `NIT Trichy`, `VIT`, `IIIT`) to filter LinkedIn search results to their college alumni working at that company.

---

## 💰 Milestone 5: Crowd-Sourced Stipend & Compensation Benchmarks

Salary transparency helps students make informed decisions.

- [ ] **Stipend Insights Column**
  - Integrate verified and community-reported India internship stipends (e.g., Google: ₹1.1L–₹1.25L/mo, Uber: ₹1.6L/mo, Microsoft: ₹1.25L/mo, Razorpay: ₹60k/mo, Swiggy: ₹50k/mo).
- [ ] **Perks & Relocation Indicators**
  - Tag benefits: Free food, company accommodation / corporate transit, travel reimbursement, hardware allowance.
- [ ] **PPO (Pre-Placement Offer) Conversion Rate Ratings**
  - Historical student ratings on how often the 2-month summer internship converts into a full-time SWE offer.

---

## 🛡️ Milestone 6: Bot Bypass & Enterprise Scraper Expansion

Bring the remaining 25 "Unsupported" companies into the automated feed.

- [ ] **SerpApi / Google Jobs Scheduled Worker**
  - Automatically query Google Jobs API for companies with closed ATS or anti-bot defenses (Flipkart, Atlassian, Uber, Zepto, D. E. Shaw).
- [ ] **Headless Browser Runner (Playwright Sidecar)**
  - Run an isolated Playwright crawler to solve Cloudflare Turnstile challenges for Apple (`jobs.apple.com`), ByteDance, and Tesla.
- [ ] **Campus Drive Aggregator (Hackerearth / Unstop / Superset)**
  - Track open-to-all national hiring challenges (Flipkart GRiD, Tata TCS NQT, Infosys Springboard, Google Girl Hackathon, Amazon ML Challenge).

---

## 🧠 Milestone 7: Interview Prep & LeetCode Intelligence

Help students transition from finding an internship to clearing the rounds.

- [ ] **Company Interview Tags & Questions**
  - Direct links to top tagged LeetCode questions for that company (e.g., Qualcomm DSA & OS/C++ tags, Google Graph/DP tags).
- [ ] **Online Assessment (OA) Pattern Guides**
  - Short summary of each company's typical screening:
    - Number of coding problems (e.g., 2 LeetCode Mediums in 60 mins).
    - Platform used (HackerRank, Codility, TestGorilla).
    - CS Fundamentals topics tested (OS, DBMS, OOPs, Computer Networks).

---

## 💡 Suggesting New Features

Have an idea that isn't listed here?
- Open a discussion or feature request in the **[GitHub Issues](https://github.com/vishnunandan555/internship-tracker/issues)** tab!
