"""
Google Flights scraping is not included in this package; FlightGrab aggregates data server-side.

For programmatic access, use :class:`flightgrab.FlightSearch` against ``https://flightgrab.cc``.
Self-hosted scraping may use libraries like ``fast-flights`` in your own code — see the
main CheapestFlights repo for reference implementations.
"""

from typing import List

from ..models import Flight
from .base import BaseScraper


class GoogleFlightsScraper(BaseScraper):
    """Placeholder — use ``FlightSearch`` for hosted data."""

    def search(self, origin: str, destination: str, date: str) -> List[Flight]:
        raise NotImplementedError(
            "Use flightgrab.FlightSearch() with FLIGHTGRAB_API_URL, or implement your own scraper."
        )
