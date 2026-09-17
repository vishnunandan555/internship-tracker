"""Shared data model for all scrapers."""
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

# Matches internship-style roles while treating underscores, hyphens and boundaries properly,
# without false-positive matching on "internal"/"international".
INTERN_RE = re.compile(
    r"(?:^|[\b_ \-\/])(intern|interns|internship|internships|co[- ]?op)(?:[\b_ \-\/]|$)",
    re.IGNORECASE,
)


def is_internship(title: str) -> bool:
    return bool(INTERN_RE.search(title))


def as_date(value) -> Optional[str]:
    """Normalize the many posted-date shapes the ATSes return to YYYY-MM-DD."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if value > 1e12:  # milliseconds
            value /= 1000.0
        if value > 1e9:
            return datetime.fromtimestamp(value, tz=timezone.utc).strftime("%Y-%m-%d")
        return None
    text = str(value).strip()
    if re.match(r"^20\d{2}-\d{2}-\d{2}", text):
        return text[:10]
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


@dataclass
class Job:
    company: str          # display name, e.g. "Google"
    external_id: str      # the ATS's own stable posting id
    title: str
    url: str              # absolute link to the job description
    locations: List[str] = field(default_factory=list)
    # Set by adapters that have a better internship signal than the title
    is_intern: Optional[bool] = None
    # Engineering role category, assigned in main.py via categories.categorize
    category: Optional[str] = None
    # Hub tag (Bengaluru, Hyderabad, Pune, Delhi-NCR, Chennai, etc.)
    city_tag: Optional[str] = None
    # Publication date (YYYY-MM-DD) from the ATS, when it exposes one
    posted: Optional[str] = None

    def looks_like_internship(self) -> bool:
        if self.is_intern is not None:
            return self.is_intern
        return is_internship(self.title)

    @property
    def uid(self) -> str:
        """Stable identity across runs: company slug + ATS posting id."""
        slug = re.sub(r"[^a-z0-9]+", "-", self.company.lower()).strip("-")
        return "{}:{}".format(slug, self.external_id)

    def to_dict(self) -> dict:
        return {
            "company": self.company,
            "external_id": str(self.external_id),
            "title": self.title.strip(),
            "url": self.url,
            "locations": sorted(set(l.strip() for l in self.locations if l and l.strip())),
            "category": self.category,
            "city_tag": self.city_tag,
            "posted": self.posted,
        }
