"""Configuration helpers."""

import os
from typing import Optional

DEFAULT_API_URL = "https://flightgrab.cc"


def get_api_url(explicit: Optional[str] = None) -> str:
    base = explicit or os.getenv("FLIGHTGRAB_API_URL") or DEFAULT_API_URL
    return base.rstrip("/")
