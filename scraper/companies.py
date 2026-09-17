"""Company registry for India Tech Internships Tracker.

Every entry: display name + adapter fetch function + adapter config.
Focuses on FAANG, top global MNC tech centers in India, and top Indian product startups/unicorns.
"""
from .adapters import (
    amazon,
    apple,
    ashby,
    bloomberg,
    eightfold,
    github_careers,
    google,
    greenhouse,
    janestreet,
    lever,
    meta,
    microsoft,
    oracle_hcm,
    phenom,
    smartrecruiters,
    spotify,
    workday,
)

# Companies we can't scrape via public JSON APIs, and why.
UNSUPPORTED = {
    "Flipkart": "careers site sits behind enterprise bot defense and routes student hiring via campus/Flipkart GRiD",
    "LinkedIn": "careers site only links to linkedin.com/jobs, which is authwalled and prohibits automated scraping",
    "Goldman Sachs": "campus & internship portal (tal.net) requires interactive SSO / browser session",
    "Uber": "careers search API sits behind Cloudflare bot protection returning 403 to non-browser clients; needs headless browser",
    "ByteDance": "job-search API rejects requests without browser client signature; needs headless browser",
    "Tesla": "careers site sits behind Akamai bot protection returning 403 to non-browser clients",
}

COMPANIES = [
    # --- FAANG & Global Big Tech ---------------------------------------------
    {"name": "Google", "fetch": google.fetch},
    {"name": "Microsoft", "fetch": microsoft.fetch},
    {"name": "Amazon", "fetch": amazon.fetch},
    {"name": "Apple", "fetch": apple.fetch},
    {"name": "Meta", "fetch": meta.fetch},
    {"name": "Netflix", "fetch": eightfold.fetch,
     "host": "explore.jobs.netflix.net", "domain": "netflix.com"},

    # --- Top Global MNC R&D Centers in India ---------------------------------
    {"name": "Adobe", "fetch": workday.fetch,
     "host": "adobe.wd5.myworkdayjobs.com", "site": "external_experienced"},
    {"name": "NVIDIA", "fetch": workday.fetch,
     "host": "nvidia.wd5.myworkdayjobs.com", "site": "NVIDIAExternalCareerSite"},
    {"name": "Salesforce", "fetch": workday.fetch,
     "host": "salesforce.wd12.myworkdayjobs.com", "site": "External_Career_Site"},
    {"name": "Cisco", "fetch": phenom.fetch, "host": "careers.cisco.com",
     "job_url": "https://careers.cisco.com/global/en/job/{id}"},
    {"name": "Intel", "fetch": workday.fetch,
     "host": "intel.wd1.myworkdayjobs.com", "site": "External"},
    {"name": "Oracle", "fetch": oracle_hcm.fetch},
    {"name": "PayPal", "fetch": workday.fetch,
     "host": "paypal.wd1.myworkdayjobs.com", "site": "jobs"},
    {"name": "ServiceNow", "fetch": smartrecruiters.fetch, "company": "servicenow"},
    {"name": "Target", "fetch": workday.fetch,
     "host": "target.wd5.myworkdayjobs.com", "site": "targetcareers"},
    {"name": "Snowflake", "fetch": phenom.fetch, "host": "careers.snowflake.com",
     "job_url": "https://careers.snowflake.com/us/en/job/{id}"},
    {"name": "GitHub", "fetch": github_careers.fetch},
    {"name": "Snap", "fetch": workday.fetch,
     "host": "snapchat.wd1.myworkdayjobs.com", "tenant": "snapchat", "site": "snap"},
    {"name": "Spotify", "fetch": spotify.fetch},

    # --- Top Indian Product Tech Startups & Unicorns -------------------------
    {"name": "Swiggy", "fetch": smartrecruiters.fetch, "company": "swiggy"},
    {"name": "Meesho", "fetch": lever.fetch, "site": "meesho"},
    {"name": "CRED", "fetch": lever.fetch, "site": "cred"},
    {"name": "Zeta", "fetch": lever.fetch, "site": "zeta"},
    {"name": "Groww", "fetch": greenhouse.fetch, "token": "groww"},
    {"name": "Slice", "fetch": greenhouse.fetch, "token": "slice"},
    {"name": "InMobi", "fetch": greenhouse.fetch, "token": "inmobi"},

    # --- Developer, Cloud & High-Growth Platforms ----------------------------
    {"name": "Stripe", "fetch": greenhouse.fetch, "token": "stripe"},
    {"name": "Coinbase", "fetch": greenhouse.fetch, "token": "coinbase"},
    {"name": "MongoDB", "fetch": greenhouse.fetch, "token": "mongodb"},
    {"name": "Datadog", "fetch": greenhouse.fetch, "token": "datadog"},
    {"name": "Cloudflare", "fetch": greenhouse.fetch, "token": "cloudflare"},
    {"name": "Databricks", "fetch": greenhouse.fetch, "token": "databricks"},
    {"name": "Figma", "fetch": greenhouse.fetch, "token": "figma"},
    {"name": "Dropbox", "fetch": greenhouse.fetch, "token": "dropbox"},

    # --- Quant & High Frequency Trading --------------------------------------
    {"name": "Jane Street", "fetch": janestreet.fetch},
    {"name": "Bloomberg", "fetch": bloomberg.fetch},
    {"name": "Hudson River Trading", "fetch": greenhouse.fetch, "token": "wehrtyou"},
]
