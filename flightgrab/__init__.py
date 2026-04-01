"""
FlightGrab — Python client for flight deal search and export.

Pro-only browser open: :func:`flightgrab.open_booking_link` (requires license or FLIGHTGRAB_PRO=1).
"""

__version__ = "0.2.1"
__author__ = "Tevin Parboosingh"
__email__ = "tparboosingh84@gmail.com"

from .booking import (
    BookingResolution,
    fetch_booking_url,
    open_booking_link,
    refresh_booking_url,
    resolve_booking,
)
from .exceptions import FlightGrabAuthError, FlightGrabError, FlightGrabProRequired
from .models import Flight, RouteStats
from .search import FlightSearch

__all__ = [
    "Flight",
    "FlightSearch",
    "RouteStats",
    "BookingResolution",
    "resolve_booking",
    "refresh_booking_url",
    "fetch_booking_url",
    "open_booking_link",
    "FlightGrabError",
    "FlightGrabProRequired",
    "FlightGrabAuthError",
    "__version__",
]
