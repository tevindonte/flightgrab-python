"""
Booking URL resolution via FlightGrab API (``/api/book-redirect?format=json``).

Airline deeplinks are short-lived; the API returns ``ttl_seconds`` and ``fallback_url``
(Google Flights search) so you can refresh or degrade gracefully.
"""

from __future__ import annotations

import os
import time
import webbrowser
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from .config import get_api_url
from .exceptions import FlightGrabProRequired
from .models import Flight


@dataclass
class BookingResolution:
    """Result of ``resolve_booking`` — primary URL plus fallback and freshness hints."""

    url: str
    fallback_url: str
    source: str
    ttl_seconds: int
    refreshed_at: str
    hint: str = ""

    def is_expired(self, fetched_at_epoch: float) -> bool:
        """
        True when ``ttl_seconds`` have passed since the client stored ``fetched_at_epoch``
        (e.g. ``time.time()`` right after :func:`resolve_booking` returned).

        Then call :func:`resolve_booking` again for a fresh ``url``, or use ``fallback_url``.
        """
        return (time.time() - fetched_at_epoch) >= float(self.ttl_seconds)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "fallback_url": self.fallback_url,
            "source": self.source,
            "ttl_seconds": self.ttl_seconds,
            "refreshed_at": self.refreshed_at,
            "hint": self.hint,
        }


def _pro_enabled(license_key: Optional[str] = None) -> bool:
    if license_key and str(license_key).strip():
        return True
    if os.getenv("FLIGHTGRAB_LICENSE_KEY"):
        return True
    if os.getenv("FLIGHTGRAB_PRO", "").strip().lower() in ("1", "true", "yes"):
        return True
    return False


def _headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """Optional X-API-Key when the server sets FLIGHTGRAB_ENFORCE_BOOKING_AUTH."""
    h: Dict[str, str] = {}
    key = api_key if api_key is not None else os.getenv("FLIGHTGRAB_BOOKING_API_KEY")
    if key and str(key).strip():
        h["X-API-Key"] = str(key).strip()
    return h


def _parse_resolution(data: Dict[str, Any]) -> BookingResolution:
    url = data.get("url")
    if not url:
        raise ValueError("book-redirect response missing url")
    return BookingResolution(
        url=str(url),
        fallback_url=str(data.get("fallback_url") or ""),
        source=str(data.get("source") or "unknown"),
        ttl_seconds=int(data.get("ttl_seconds") or 600),
        refreshed_at=str(data.get("refreshed_at") or ""),
        hint=str(data.get("hint") or ""),
    )


def resolve_booking(
    origin: str,
    destination: str,
    departure_date: str,
    api_url: Optional[str] = None,
    timeout: float = 60.0,
    api_key: Optional[str] = None,
) -> BookingResolution:
    """
    Call the API and return structured booking data: primary ``url``, ``fallback_url``,
    ``ttl_seconds`` (heuristic), and ``source`` (how the URL was obtained).

    If the primary link stops working after ~``ttl_seconds``, call ``resolve_booking`` again
    for a fresh URL, or send users to ``fallback_url`` (Google Flights search).

    Pass ``api_key`` (or set ``FLIGHTGRAB_BOOKING_API_KEY``) when the server enforces booking auth.
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
        headers=_headers(api_key),
        timeout=timeout,
    )
    r.raise_for_status()
    return _parse_resolution(r.json())


def fetch_booking_url(
    origin: str,
    destination: str,
    departure_date: str,
    api_url: Optional[str] = None,
    timeout: float = 60.0,
    api_key: Optional[str] = None,
) -> str:
    """Return only the primary booking URL (same as ``resolve_booking(...).url``)."""
    return resolve_booking(
        origin, destination, departure_date, api_url=api_url, timeout=timeout, api_key=api_key
    ).url


def refresh_booking_url(
    origin: str,
    destination: str,
    departure_date: str,
    api_url: Optional[str] = None,
    timeout: float = 60.0,
    api_key: Optional[str] = None,
) -> BookingResolution:
    """Alias for :func:`resolve_booking` — use when intentionally fetching a fresh link."""
    return resolve_booking(
        origin, destination, departure_date, api_url=api_url, timeout=timeout, api_key=api_key
    )


def open_booking_link(
    flight: Flight,
    api_url: Optional[str] = None,
    license_key: Optional[str] = None,
    timeout: float = 60.0,
    use_fallback: bool = False,
    api_key: Optional[str] = None,
) -> BookingResolution:
    """
    Resolve URLs and open one in the default browser (Pro-gated).

    Opens ``fallback_url`` instead of ``url`` when ``use_fallback=True`` (e.g. primary expired).
    """
    if not _pro_enabled(license_key):
        raise FlightGrabProRequired()
    res = resolve_booking(
        flight.origin,
        flight.destination,
        flight.departure_date,
        api_url=api_url,
        timeout=timeout,
        api_key=api_key,
    )
    open_url = res.fallback_url if use_fallback and res.fallback_url else res.url
    webbrowser.open(open_url)
    return res


def open_fallback_search(
    flight: Flight,
    api_url: Optional[str] = None,
    license_key: Optional[str] = None,
    timeout: float = 60.0,
    api_key: Optional[str] = None,
) -> BookingResolution:
    """Pro-gated: open ``fallback_url`` (Google Flights search) from a fresh resolution."""
    return open_booking_link(
        flight,
        api_url=api_url,
        license_key=license_key,
        timeout=timeout,
        use_fallback=True,
        api_key=api_key,
    )
