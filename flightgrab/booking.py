"""
Pro-oriented helpers: resolve a fresh booking URL and optionally open the system browser.

Free tier: use ``Flight.booking_url`` from search results.

Pro (or local dev): set ``FLIGHTGRAB_LICENSE_KEY`` or ``FLIGHTGRAB_PRO=1``, then call
``open_booking_link`` / ``fetch_booking_url``.
"""

import os
import webbrowser
from typing import Optional

import requests

from .config import get_api_url
from .exceptions import FlightGrabProRequired
from .models import Flight


def _pro_enabled(license_key: Optional[str] = None) -> bool:
    if license_key and str(license_key).strip():
        return True
    if os.getenv("FLIGHTGRAB_LICENSE_KEY"):
        return True
    if os.getenv("FLIGHTGRAB_PRO", "").strip().lower() in ("1", "true", "yes"):
        return True
    return False


def fetch_booking_url(
    origin: str,
    destination: str,
    departure_date: str,
    api_url: Optional[str] = None,
    timeout: float = 60.0,
) -> str:
    """
    Return a redirect URL (airline or Google Flights) via ``/api/book-redirect?format=json``.

    This does not require Pro; use it to build your own UX without opening a browser.
    """
    base = get_api_url(api_url)
    r = requests.get(
        f"{base}/api/book-redirect",
        params={
            "origin": origin.upper()[:3],
            "destination": destination.upper()[:3],
            "date": departure_date,
            "format": "json",
        },
        timeout=timeout,
    )
    r.raise_for_status()
    data = r.json()
    url = data.get("url")
    if not url:
        raise ValueError("book-redirect response missing url")
    return url


def open_booking_link(
    flight: Flight,
    api_url: Optional[str] = None,
    license_key: Optional[str] = None,
    timeout: float = 60.0,
) -> str:
    """
    Resolve a fresh booking URL and open it in the default browser.

    Gated as a **Pro** feature: set ``FLIGHTGRAB_LICENSE_KEY``, or ``FLIGHTGRAB_PRO=1``
    for local development.
    """
    if not _pro_enabled(license_key):
        raise FlightGrabProRequired()
    url = fetch_booking_url(
        flight.origin,
        flight.destination,
        flight.departure_date,
        api_url=api_url,
        timeout=timeout,
    )
    webbrowser.open(url)
    return url
