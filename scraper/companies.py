"""Company registry for India Tech Internships Tracker.

Every entry: display name + adapter fetch function + adapter config.
Focuses on FAANG, top global MNC tech centers in India, and top Indian product startups/unicorns.
"""
from .adapters import (
    amazon,
    amd,
    apple,
    ashby,
    bloomberg,
    eightfold,
    github_careers,
    google,
    greenhouse,
    lever,
    meta,
    microsoft,
    oracle_hcm,
    phenom,
    qualcomm,
    smartrecruiters,
    workday,
)

# Companies we can't scrape via public JSON APIs, and why.
UNSUPPORTED = {
    # Tier A
    "Atlassian": "careers site uses iCIMS iframe portal without public search API; student hiring routed via campus and early-career portal",
    # Tier B
    "BrowserStack": "uses closed ATS without public search API; routes student hiring via campus & aggregators",
    "Chargebee": "uses closed ATS without public search API; routes student hiring via campus & aggregators",
    "Dream11": "uses Dream Sports proprietary careers portal without public search API",
    "Flipkart": "careers site sits behind enterprise bot defense and routes student hiring via campus visits & Flipkart GRiD",
    "Postman": "retired public Greenhouse board; careers site runs custom Next.js frontend without public search API",
    "Zepto": "uses TalentRecruit proprietary portal without public search API; hires via campus & portal forms",
    "Zerodha": "no external ATS; engineering openings posted ad-hoc via static page (zerodha.com/careers) and email",
    "Zoho": "uses Zoho Recruit proprietary portal without public job search API",
    # Tier C
    "Arm": "early careers portal (earlycareers-arm.icims.com) requires authenticated candidate login",
    "HP": "careers portal sits behind Cloudflare bot protection returning 403 to non-browser clients",
    "Intuit": "careers portal sits behind Radancy search without open public REST API",
    "SAP": "SuccessFactors career site requires authenticated recruiter operators; no public search API",
    "Siemens": "careers site runs on Avature global portal without public JSON search API; requires interactive session",
    "Faveo": "careers site runs on Zoho Recruit India portal without open unauthenticated REST API",
    "Uber": "careers search API sits behind Cloudflare bot protection returning 403 to non-browser clients; needs headless browser",
    # Tier D
    "American Express": "careers site sits behind Akamai bot defense returning 403 to automated clients",
    "D. E. Shaw": "campus-only hiring program for Indian engineering colleges (IIT/BITS/NIT)",
    "Deloitte": "South Asia career portal runs on closed SAP SuccessFactors infrastructure; routes graduate hiring via campus",
    "Goldman Sachs": "campus & internship portal (tal.net) requires interactive SSO / browser session",
    "Infosys": "student tech hiring conducted exclusively through InfyTQ / Springboard campus portal",
    "Tata Consultancy Services": "student tech hiring conducted exclusively through TCS NextStep / National Qualifier Test (NQT) campus portal",
    # Other Notable
    "ByteDance": "job-search API rejects requests without browser client signature; needs headless browser",
    "LinkedIn": "careers site only links to linkedin.com/jobs, which is authwalled and prohibits automated scraping",
    "Target": "US retail company with no India engineering center; scraper returns 0 India listings across 300+ postings",
    "Tesla": "careers site sits behind Akamai bot protection returning 403 to non-browser clients",
}

COMPANIES = [
    # --- Tier A: Major Product / Big Tech ------------------------------------
    {"name": "Google", "fetch": google.fetch},
    {"name": "Microsoft", "fetch": microsoft.fetch},
    {"name": "Amazon", "fetch": amazon.fetch},
    {"name": "Apple", "fetch": apple.fetch},
    {"name": "Adobe", "fetch": workday.fetch,
     "host": "adobe.wd5.myworkdayjobs.com", "site": "external_experienced"},
    {"name": "Salesforce", "fetch": workday.fetch,
     "host": "salesforce.wd12.myworkdayjobs.com", "site": "External_Career_Site",
     "search_text": "internship"},
    {"name": "Oracle", "fetch": oracle_hcm.fetch},
    {"name": "NVIDIA", "fetch": workday.fetch,
     "host": "nvidia.wd5.myworkdayjobs.com", "site": "NVIDIAExternalCareerSite"},
    {"name": "Qualcomm", "fetch": qualcomm.fetch},
    {"name": "Meta", "fetch": meta.fetch},
    {"name": "Netflix", "fetch": eightfold.fetch,
     "host": "explore.jobs.netflix.net", "domain": "netflix.com"},

    # --- Tier B: Strong Product / Indian Tech Unicorns -----------------------
    {"name": "PhonePe", "fetch": smartrecruiters.fetch, "company": "PHONEPELIMITED"},
    {"name": "Razorpay", "fetch": greenhouse.fetch, "token": "razorpaysoftwareprivatelimited"},
    {"name": "Freshworks", "fetch": smartrecruiters.fetch, "company": "freshworks"},
    {"name": "Swiggy", "fetch": smartrecruiters.fetch, "company": "swiggy"},
    {"name": "Meesho", "fetch": lever.fetch, "site": "meesho"},
    {"name": "CRED", "fetch": lever.fetch, "site": "cred"},
    {"name": "Groww", "fetch": greenhouse.fetch, "token": "groww"},
    {"name": "Zeta", "fetch": lever.fetch, "site": "zeta"},
    {"name": "InMobi", "fetch": greenhouse.fetch, "token": "inmobi"},

    # --- Tier C: Global Tech MNCs & India Engineering Centers / GCCs --------
    {"name": "Walmart Global Tech", "fetch": workday.fetch,
     "host": "walmart.wd504.myworkdayjobs.com", "site": "WalmartExternal"},
    {"name": "Dell Technologies", "fetch": oracle_hcm.fetch,
     "host": "enterpriseplatform.dell.com", "site_number": "CX_1",
     "job_url": "https://enterpriseplatform.dell.com/hcmUI/CandidateExperience/en/sites/CX_1/job/{id}"},
    {"name": "Cisco", "fetch": phenom.fetch, "host": "careers.cisco.com",
     "job_url": "https://careers.cisco.com/global/en/job/{id}"},
    {"name": "Intel", "fetch": workday.fetch,
     "host": "intel.wd1.myworkdayjobs.com", "site": "External"},
    {"name": "AMD", "fetch": amd.fetch},
    {"name": "Red Hat", "fetch": workday.fetch,
     "host": "redhat.wd5.myworkdayjobs.com", "site": "jobs",
     "search_text": "internship"},
    {"name": "HPE", "fetch": phenom.fetch, "host": "careers.hpe.com",
     "job_url": "https://careers.hpe.com/us/en/job/{id}"},
    {"name": "Broadcom (VMware)", "fetch": workday.fetch,
     "host": "broadcom.wd1.myworkdayjobs.com", "site": "External_Career"},
    {"name": "PayPal", "fetch": workday.fetch,
     "host": "paypal.wd1.myworkdayjobs.com", "site": "jobs"},
    {"name": "ServiceNow", "fetch": smartrecruiters.fetch, "company": "servicenow"},
    {"name": "Nokia", "fetch": oracle_hcm.fetch,
     "host": "fa-evmr-saasfaprod1.fa.ocs.oraclecloud.com", "site_number": "CX_1",
     "job_url": "https://fa-evmr-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/job/{id}"},
    {"name": "Snowflake", "fetch": phenom.fetch, "host": "careers.snowflake.com",
     "job_url": "https://careers.snowflake.com/us/en/job/{id}"},
    {"name": "GitHub", "fetch": github_careers.fetch},

    # --- Tier D: Finance / Enterprise Engineering Centers --------------------
    {"name": "JPMorgan Chase", "fetch": oracle_hcm.fetch,
     "host": "jpmc.fa.oraclecloud.com", "site_number": "CX_1001",
     "job_url": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/{id}"},
    {"name": "Accenture", "fetch": workday.fetch,
     "host": "accenture.wd103.myworkdayjobs.com", "site": "AccentureCareers"},
    {"name": "Wells Fargo", "fetch": workday.fetch,
     "host": "wf.wd1.myworkdayjobs.com", "tenant": "wf", "site": "WellsFargoJobs"},
    {"name": "Morgan Stanley", "fetch": workday.fetch,
     "host": "ms.wd5.myworkdayjobs.com", "tenant": "ms", "site": "External"},
    {"name": "Bloomberg", "fetch": bloomberg.fetch},

    # --- Developer & High-Growth Platforms in India --------------------------
    {"name": "Stripe", "fetch": greenhouse.fetch, "token": "stripe"},
    {"name": "MongoDB", "fetch": greenhouse.fetch, "token": "mongodb"},
    {"name": "Rubrik", "fetch": greenhouse.fetch, "token": "rubrik"},
]
