"""
Live Google Flights results via ``fast-flights`` (optional dependency).

Install: ``pip install flightgrab[local]``
"""

from __future__ import annotations

import urllib.parse
from typing import List, Optional

from .models import Flight
from .utils import parse_duration_minutes


def _parse_price(price_str) -> Optional[float]:
    if not price_str or not isinstance(price_str, str):
        return None
    s = price_str.strip().replace("$", "").replace(",", "").replace(" ", "")
    if not s or s.lower() in ("unavailable", "n/a", "na", "price unavailable"):
        return None
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _parse_stops(value) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _google_flights_search_url(origin: str, destination: str, date: str) -> str:
    base = "https://www.google.com/travel/flights"
    q = f"Flights from {origin} to {destination} on {date}"
    return f"{base}?q={urllib.parse.quote(q)}"


def find_flights_local(
    origin: str,
    destination: str,
    date: str,
    limit: int = 50,
) -> List[Flight]:
    """
    Scrape Google Flights in-process using ``fast-flights``. No FlightGrab server required.

    Rate limits and breakage follow the ``fast-flights`` library; not suitable for high-volume
    server use — intended for local scripts and the ``backend='local'`` client mode.
    """
    try:
        from fast_flights import FlightData, Passengers, get_flights
    except ImportError as e:
        raise ImportError(
            "Local search requires fast-flights. Install: pip install flightgrab[local]"
        ) from e

    origin, destination = origin.upper()[:3], destination.upper()[:3]
    result = get_flights(
        flight_data=[FlightData(date=date, from_airport=origin, to_airport=destination)],
        trip="one-way",
        seat="economy",
        passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
    )
    if not result or not result.flights:
        return []

    booking_base = _google_flights_search_url(origin, destination, date)
    out: List[Flight] = []
    for f in result.flights[: max(limit, 1)]:
        price = _parse_price(getattr(f, "price", None))
        if price is None:
            continue
        dur = getattr(f, "duration", None) or ""
        out.append(
            Flight(
                price=price,
                airline=(getattr(f, "name", None) or "") or "",
                origin=origin,
                destination=destination,
                departure_date=date,
                departure_time=(getattr(f, "departure", None) or "") or "",
                arrival_time=(getattr(f, "arrival", None) or "") or "",
                duration_minutes=parse_duration_minutes(dur) if isinstance(dur, str) else 0,
                stops=_parse_stops(getattr(f, "stops", 0)),
                booking_url=booking_base,
            )
        )

    out.sort(key=lambda x: (x.price, x.departure_time))
    return out
