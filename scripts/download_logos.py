#!/usr/bin/env python3
"""Download high-resolution official brand logos for all 55 tracked companies into docs/logos/."""
import os
import re
import urllib.request
from typing import Dict

COMPANY_DOMAINS: Dict[str, str] = {
    "Google": "google.com",
    "Microsoft": "microsoft.com",
    "Amazon": "amazon.com",
    "Apple": "apple.com",
    "Adobe": "adobe.com",
    "Salesforce": "salesforce.com",
    "Oracle": "oracle.com",
    "NVIDIA": "nvidia.com",
    "Qualcomm": "qualcomm.com",
    "Meta": "meta.com",
    "Netflix": "netflix.com",
    "PhonePe": "phonepe.com",
    "Razorpay": "razorpay.com",
    "Freshworks": "freshworks.com",
    "Swiggy": "swiggy.com",
    "Meesho": "meesho.com",
    "CRED": "cred.club",
    "Groww": "groww.in",
    "Zeta": "zeta.tech",
    "InMobi": "inmobi.com",
    "Zomato": "zomato.com",
    "Walmart Global Tech": "walmart.com",
    "Dell Technologies": "dell.com",
    "Cisco": "cisco.com",
    "Intel": "intel.com",
    "AMD": "amd.com",
    "Red Hat": "redhat.com",
    "HPE": "hpe.com",
    "Broadcom (VMware)": "broadcom.com",
    "PayPal": "paypal.com",
    "ServiceNow": "servicenow.com",
    "CrowdStrike": "crowdstrike.com",
    "Palo Alto Networks": "www.paloaltonetworks.com",
    "Workday": "workday.com",
    "Micron": "micron.com",
    "Nokia": "nokia.com",
    "Snowflake": "snowflake.com",
    "GitHub": "github.com",
    "JPMorgan Chase": "jpmorganchase.com",
    "Accenture": "accenture.com",
    "Wells Fargo": "wellsfargo.com",
    "Morgan Stanley": "morganstanley.com",
    "Barclays": "barclays.com",
    "Visa": "visa.com",
    "Mastercard": "mastercard.com",
    "Bloomberg": "bloomberg.com",
    "Stripe": "stripe.com",
    "MongoDB": "mongodb.com",
    "Rubrik": "rubrik.com",
    "Cloudflare": "cloudflare.com",
    "Datadog": "datadoghq.com",
    "Databricks": "databricks.com",
    "Elastic": "elastic.co",
    "GitLab": "gitlab.com",
    "Twilio": "twilio.com",
}

# High-resolution overrides for companies where standard favicon is 16x16
CUSTOM_URLS: Dict[str, str] = {
    "AMD": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/AMD_Logo.svg/120px-AMD_Logo.svg.png",
    "Cisco": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Cisco_logo_blue_2016.svg/120px-Cisco_logo_blue_2016.svg.png",
}


def slugify(name: str) -> str:
    """Normalize company name to lowercase slug matching frontend convention."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def download_all_logos() -> None:
    dest_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "logos"))
    os.makedirs(dest_dir, exist_ok=True)

    print(f"Downloading logos for {len(COMPANY_DOMAINS)} companies into: {dest_dir}")
    success = 0
    failed = []

    for name, domain in COMPANY_DOMAINS.items():
        slug = slugify(name)
        dest_path = os.path.join(dest_dir, f"{slug}.png")

        if name in CUSTOM_URLS:
            url = CUSTOM_URLS[name]
        else:
            url = f"https://t2.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=https://{domain}&size=128"

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = resp.read()
                if len(data) > 100:
                    with open(dest_path, "wb") as fh:
                        fh.write(data)
                    success += 1
                    print(f"  ✓ {name:25} -> {slug}.png ({len(data)} bytes)")
                else:
                    failed.append((name, f"Payload too small: {len(data)} bytes"))
        except Exception as exc:
            failed.append((name, str(exc)))
            print(f"  ✗ {name:25} Error: {exc}")

    print(f"\nCompleted: {success}/{len(COMPANY_DOMAINS)} logos downloaded successfully.")
    if failed:
        print(f"Failures ({len(failed)}): {failed}")


if __name__ == "__main__":
    download_all_logos()
