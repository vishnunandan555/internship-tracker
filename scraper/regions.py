"""India location filter and city classifier.

Location strings come in many ATS shapes ("Bengaluru, Karnataka, India",
"Bangalore", "Hyderabad, Telangana", "Remote - India", "India, Multiple Locations", ...).

Algorithm per location:
1. Explicit NON-India country / state / city -> reject
   (Prevents false positives like "Indiana, USA", "Indianapolis", "Indonesia", "London, UK")
2. Explicit India keyword / country / ISO code / Indian State -> accept
3. Well-known Indian city / tech hub -> accept
4. Otherwise -> reject

A job counts as an India job when ANY of its locations passes.
"""
import re


def _rx(words):
    return re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b", re.IGNORECASE)


# Exclude words that could conflict with "IN" / "Ind" or resemble India
NON_INDIA = re.compile(
    r"\b("
    r"Indiana|Indianapolis|Indio|Indonesia|Jakarta|Bali|Indo[- ]?Pacific|"
    r"United States|USA|U\.S\.|Canada|United Kingdom|UK|England|London|"
    r"Germany|Deutschland|Berlin|Munich|France|Paris|Australia|Sydney|Melbourne|"
    r"Singapore|Japan|Tokyo|China|Beijing|Shanghai|Ireland|Dublin|"
    r"Netherlands|Amsterdam|Switzerland|Zurich|Poland|Warsaw|Sweden|Stockholm|"
    r"Brazil|Sao Paulo|Mexico|Israel|Tel Aviv|Spain|Madrid|Barcelona|"
    r"Taiwan|South Korea|Seoul|Hong Kong|Dubai|UAE|Saudi Arabia|"
    r"CAN|USA|GBR|DEU|FRA|AUS|SGP|JPN|CHN|IRL|NLD|CHE|POL|SWE|BRA|MEX|ISR|ESP|TWN|KOR|HKG|ARE|SAU"
    r")\b",
    re.IGNORECASE,
)

INDIA_COUNTRY_OR_STATE = _rx([
    "India", "IND", "Bharat",
    # States & Union Territories
    "Karnataka", "Telangana", "Maharashtra", "Tamil Nadu", "Tamilnadu",
    "Haryana", "Uttar Pradesh", "UP", "Delhi", "New Delhi", "Delhi NCR", "NCR",
    "Kerala", "West Bengal", "Gujarat", "Rajasthan", "Punjab", "Madhya Pradesh",
    "Andhra Pradesh", "AP", "Odisha", "Orissa", "Assam", "Goa", "Chandigarh",
    "Uttarakhand", "Jharkhand", "Bihar",
])

INDIA_CITIES = _rx([
    # Tier 1 Tech Hubs
    "Bengaluru", "Bangalore", "BLR",
    "Hyderabad", "HYD", "Secunderabad", "Cyberabad",
    "Pune", "PUN",
    "Gurugram", "Gurgaon", "GGN",
    "Noida", "Greater Noida",
    "Delhi", "New Delhi",
    "Chennai", "Madras", "MAA",
    "Mumbai", "Bombay", "BOM", "Navi Mumbai", "Thane",
    # Tier 2 Tech Hubs
    "Kolkata", "Calcutta",
    "Ahmedabad", "Gandhinagar",
    "Kochi", "Cochin",
    "Thiruvananthapuram", "Trivandrum",
    "Coimbatore",
    "Indore",
    "Jaipur",
    "Chandigarh", "Mohali", "Panchkula",
    "Bhubaneswar",
    "Mysuru", "Mysore",
    "Nagpur",
    "Visakhapatnam", "Vizag",
    "Vadodara", "Baroda",
    "Surat",
    "Mangalore", "Mangaluru",
    "Vijayawada",
    "Lucknow",
    "Kanpur",
    "Bhopal",
    "Dehradun",
])

REMOTE_INDIA = re.compile(
    r"\b(remote\s*[-–—]?\s*india|india\s*[-–—]?\s*remote|anywhere\s+in\s+india|work\s+from\s+home\s*[-–—]?\s*india)\b",
    re.IGNORECASE,
)


def _is_indian_location(text):
    if not text or not text.strip():
        return False
    text = text.strip()

    # Remote explicitly in India
    if REMOTE_INDIA.search(text):
        return True

    # If it contains an explicit foreign country without mentioning India
    if NON_INDIA.search(text) and not re.search(r"\b(india|ind)\b", text, re.IGNORECASE):
        return False

    if INDIA_COUNTRY_OR_STATE.search(text):
        return True

    return bool(INDIA_CITIES.search(text))


def is_india_job(locations):
    return any(_is_indian_location(loc) for loc in locations if loc)


# Ordered mapping of target UI hub tags to identifying location keywords.
CITY_TAG_RULES: tuple = (
    ("Bengaluru", ("bengaluru", "bangalore", "blr")),
    ("Hyderabad", ("hyderabad", "secunderabad", "cyberabad")),
    ("Pune", ("pune",)),
    ("Delhi-NCR", ("gurugram", "gurgaon", "noida", "delhi", "ncr")),
    ("Chennai", ("chennai",)),
    ("Mumbai", ("mumbai", "thane", "navi mumbai")),
)


def get_city_tag(locations):
    """Classify into standard UI filter tags: bengaluru, hyderabad, pune, ncr, chennai, mumbai, remote, other."""
    combined = " ".join(locations or []).lower()
    # Explicit parentheses: REMOTE_INDIA pattern matches directly, OR a generic "remote" string
    # is verified to actually be an Indian location (avoiding matching US/global-only remote roles).
    if REMOTE_INDIA.search(combined) or ("remote" in combined and is_india_job(locations)):
        return "Remote (India)"

    for tag, keywords in CITY_TAG_RULES:
        if any(kw in combined for kw in keywords):
            return tag

    return "India (Multiple/Other)"

