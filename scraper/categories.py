"""Software and tech engineering role classifier for India Tech Internships.

The tracker lists tech engineering internships: AI/ML, Data, Mobile, Frontend,
Backend/Infra, Software (SWE/SDE/MTS), Hardware/Silicon, QA, Security.
categorize() returns the category for a title, or None for out-of-scope roles
(sales, HR, finance, legal, marketing, operations, ...) which are then dropped.

Order matters: first matching category wins, so the more specific ones
(Security, QA, Hardware/Silicon, Mobile, ...) come before the catch-alls.
"""
import re
from typing import Optional


def _rx(pattern):
    return re.compile(pattern, re.IGNORECASE)


# Unambiguous engineering-role signals in India tech roles (SDE, MTS, SWE, Silicon, etc.).
HARD_INCLUDE_RE = _rx(
    r"software|machine learning|deep learning|computer vision|"
    r"applied scien|research scien|data scien|data engineer|data analy|"
    r"full[- ]?stack|front[- ]?end|back[- ]?end|\bios\b|android|\bsdet\b|"
    r"security engineer|cybersecurity|\bnlp\b|\bllm\b|compiler|kernel|"
    r"\bsde\b|\bmts\b|\bswe\b|\bsw\b|_sw\b|_sw_|\bhw\b|_hw\b|_hw_|"
    r"graduate engineer trainee|\bget\b|technology intern|technical intern|"
    r"grad(uate)? intern|college intern|engineering intern|"
    r"firmware|embedded|systems engineer|silicon|asic|vlsi|fpga"
)

# Roles that pattern-match a keyword but aren't tech/software engineering work.
EXCLUDE_RE = _rx(
    r"technician|data cent(er|re)|solutions? engineer|sales|account manag|"
    r"customer success|field engineer|facilities|construction|mechanical|"
    r"civil engineer|manufacturing|supply chain|operations manager|"
    r"process engineer|industrial engineer|recruiter|talent acquisition|marketing|"
    r"human resources|\bhr\b|finance|legal|counsel|accountant|warehouse"
)

# Ordered definition table: (identifier, display_name, raw_regex_pattern)
_CATEGORY_DEFS = [
    ("Security", "Security", r"security|cyber|infosec|appsec|threat|penetration|red team|vulnerab|crypto(graph|log)"),
    ("QA", "QA", r"\bqa\b|quality (assurance|engineer)|test(ing)? engineer|software test|\bsdet\b|validation"),
    ("AIML", "AI/ML", r"\bai\b|artificial intelligence|machine learning|\bml\b|deep learning|computer vision|\bnlp\b|\bllm\b|gen ?ai|generative|applied scien|research scien|research engineer|student researcher|robotics|autonom|perception|recommender|applied scientist|research scientist"),
    ("Data", "Data", r"\bdata\b|analytics|business intelligence|bi engineer"),
    ("HardwareSilicon", "Hardware/Silicon", r"silicon|hardware|\bhw\b|_hw\b|_hw_|asic|vlsi|fpga|semiconductor|circuit"),
    ("Mobile", "Mobile", r"mobile|\bios\b|android|flutter|react native"),
    ("Frontend", "Frontend", r"front[- ]?end|web develop|web engineer|\bui engineer\b|javascript|typescript|\breact\b"),
    ("BackendInfra", "Backend/Infra", r"back[- ]?end|distributed|infrastructure|platform|cloud|devops|site reliability|\bsre\b|\bapi\b|database|storage|network|linux|kernel|embedded|firmware|compiler|operating system|virtualization"),
    ("Software", "Software", r"software|\bswe\b|\bsde\b|\bmts\b|\bsw\b|_sw\b|_sw_|developer|full[- ]?stack|programmer|application develop|computer science|solution develop|game develop|\bdev\b|\bjava\b|\bpython\b|c\+\+|\bgolang\b|\brust\b|graduate engineer trainee|\bget\b|technical intern|technology intern|engineering intern|grad(uate)? intern|college intern"),
]

GROUP_TO_CATEGORY = {grp: cat for grp, cat, _ in _CATEGORY_DEFS}

# Combined single-pass regex compiled with named groups for fast O(1) matching
COMBINED_CATEGORIES_RE = re.compile(
    "|".join(f"(?P<{grp}>{pat})" for grp, _, pat in _CATEGORY_DEFS),
    re.IGNORECASE,
)

# Retained for backwards-compatibility with existing tests and imports
CATEGORIES = [(cat, _rx(pat)) for _, cat, pat in _CATEGORY_DEFS]


def categorize(title: str) -> Optional[str]:
    """Classify an internship title into a tech category, or return None if out-of-scope."""
    if not title:
        return None
    if not HARD_INCLUDE_RE.search(title) and EXCLUDE_RE.search(title):
        return None
    m = COMBINED_CATEGORIES_RE.search(title)
    if m and m.lastgroup:
        return GROUP_TO_CATEGORY.get(m.lastgroup)
    if HARD_INCLUDE_RE.search(title):
        return "Software"
    return None

