from __future__ import annotations
import re
from typing import Set

APN_DIGITS_RE = re.compile(r"\D+")

def normalize_apn(value):
    """Return APN with only digits, or None if nothing remains."""
    if value is None:
        return None
    s = str(value)
    digits = APN_DIGITS_RE.sub("", s)
    return digits if digits else None

# Only these statuses are allowed
ALLOWED_STATUSES: Set[str] = {"for_sale", "pending", "sold"}
