"""Shared helpers."""

import re


def parse_duration_minutes(duration: str) -> int:
    """Parse strings like '5h 30m' or '2h' into minutes."""
    if not duration or not isinstance(duration, str):
        return 0
    s = duration.strip().lower()
    total = 0
    hm = re.search(r"(\d+)\s*h", s)
    mm = re.search(r"(\d+)\s*m", s)
    if hm:
        total += int(hm.group(1)) * 60
    if mm:
        total += int(mm.group(1))
    return total
