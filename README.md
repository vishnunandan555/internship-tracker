# 🇮🇳 Software Engineering & Tech Internship Tracker — India

Auto-updated list of **open tech & software-engineering internships in India** —
AI/ML, Data, Full-Stack, Backend, Frontend, Mobile, QA/SDET, and Security roles — at
37 top tech companies, GCCs, and high-growth Indian unicorns. Scraped directly
from official careers APIs every 3 hours by GitHub Actions.

🌐 **Live Web Dashboard: [vishnunandan555.github.io/internship-tracker](https://vishnunandan555.github.io/internship-tracker/)**

> 🕐 Last updated: **2026-09-17 15:57:46 UTC** · 📌 **7** open internships
> · 🆕 = added in the last 7 days

⭐ Star this repository to keep track of new openings — or watch *Activity* for commits titled “new internship(s)”.

| Company | Open Internships in India |
|---|:---:|
| Adobe | — |
| Amazon | — |
| Apple | — |
| Bloomberg | — |
| CRED | — |
| Cisco | — |
| Cloudflare | — |
| Coinbase | — |
| Databricks | — |
| Datadog | — |
| Dropbox | — |
| Figma | — |
| GitHub | — |
| [Google](#google) | **1** |
| Groww | — |
| Hudson River Trading | — |
| InMobi | — |
| Intel | — |
| Jane Street | — |
| Meesho | — |
| Meta | — |
| [Microsoft](#microsoft) | **4** |
| MongoDB | — |
| [NVIDIA](#nvidia) | **1** |
| Netflix | — |
| Oracle | — |
| PayPal | — |
| Salesforce | — |
| ServiceNow | — |
| Slice | — |
| Snap | — |
| Snowflake | — |
| Spotify | — |
| [Stripe](#stripe) | **1** |
| Swiggy | — |
| Target | — |
| Zeta | — |
| ByteDance | *job-search API rejects requests without browser client signature; needs headless browser* |
| Flipkart | *careers site sits behind enterprise bot defense and routes student hiring via campus/Flipkart GRiD* |
| Goldman Sachs | *campus & internship portal (tal.net) requires interactive SSO / browser session* |
| LinkedIn | *careers site only links to linkedin.com/jobs, which is authwalled and prohibits automated scraping* |
| Tesla | *careers site sits behind Akamai bot protection returning 403 to non-browser clients* |
| Uber | *careers search API sits behind Cloudflare bot protection returning 403 to non-browser clients; needs headless browser* |

---

## Google

| Role | Category | Hub / Location | Posted | First seen |
|---|---|---|---|---|
| [Software Engineering PhD Intern, Summer 2027](https://www.google.com/about/careers/applications/jobs/results/109976286780105414) 🆕 | Software | Bengaluru | 2026-09-07 | 2026-09-17 |

## Microsoft

| Role | Category | Hub / Location | Posted | First seen |
|---|---|---|---|---|
| [Applied Sciences INTERN](https://apply.careers.microsoft.com/careers/job/1970393556997800) 🆕 | AI/ML | India (Multiple/Other) | 2026-09-14 | 2026-09-17 |
| [Software Engineering INTERN](https://apply.careers.microsoft.com/careers/job/1970393556911730) 🆕 | Software | India (Multiple/Other) | 2026-08-28 | 2026-09-17 |
| [Research Sciences INTERN](https://apply.careers.microsoft.com/careers/job/1970393556971804) 🆕 | AI/ML | Bengaluru | 2026-08-20 | 2026-09-17 |
| [Research Sciences INTERN](https://apply.careers.microsoft.com/careers/job/1970393556641091) 🆕 | AI/ML | India (Multiple/Other) | 2026-02-27 | 2026-09-17 |

## NVIDIA

| Role | Category | Hub / Location | Posted | First seen |
|---|---|---|---|---|
| [PhD Intern, AI ML in Wireless L1/L2 - Fall 2026](https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/India-Bengaluru/PhD-Intern--AI-ML-in-Wireless-L1-L2---Fall-2026_JR2024423) 🆕 | AI/ML | Bengaluru | 2026-08-31 | 2026-09-17 |

## Stripe

| Role | Category | Hub / Location | Posted | First seen |
|---|---|---|---|---|
| [Software Engineer, Intern](https://stripe.com/jobs/search?gh_jid=8031833) 🆕 | Software | Bengaluru | 2026-07-10 | 2026-09-17 |


---

## ⚙️ How This Works

A [Python scraper](scraper/) runs in GitHub Actions every 3 hours:
1. Queries official careers APIs (Workday, Greenhouse, SmartRecruiters, Lever, Eightfold, Phenom, and in-house REST APIs).
2. Filters for active internships, co-ops, and trainee software roles ([scraper/categories.py](scraper/categories.py)).
3. Strictly filters locations within India tech hubs (Bengaluru, Hyderabad, Pune, Delhi-NCR, Chennai, Mumbai, and Remote India) ([scraper/regions.py](scraper/regions.py)).
4. Diffs against [`data/jobs.json`](data/jobs.json) to track additions, closures, and re-openings.
5. Auto-updates this `README.md` and the interactive web dashboard in `docs/`.

Found an issue or want to request a company? Feel free to open an issue or pull request!
