"""
FlightGrab — Python client for flight deal search and export.

Pro-only browser open: :func:`flightgrab.open_booking_link` (requires license or FLIGHTGRAB_PRO=1).
"""

__version__ = "0.1.0"
__author__ = "Tevin Parboosingh"
__email__ = "tparboosingh84@gmail.com"

from .booking import fetch_booking_url, open_booking_link
from .exceptions import FlightGrabAuthError, FlightGrabError, FlightGrabProRequired
from .models import Flight, RouteStats
from .search import FlightSearch

__all__ = [
    "Flight",
    "FlightSearch",
    "RouteStats",
    "fetch_booking_url",
    "open_booking_link",
    "FlightGrabError",
    "FlightGrabProRequired",
    "FlightGrabAuthError",
    "__version__",
]
