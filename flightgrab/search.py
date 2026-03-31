"""HTTP client for FlightGrab public APIs."""

import csv
import json
import os
from typing import Any, Dict, List, Optional

import requests

from .config import get_api_url
from .exceptions import FlightGrabAuthError, FlightGrabError
from .models import Flight, RouteStats


class FlightSearch:
    """
    Search flights: ``backend='api'`` (default) uses FlightGrab stored data; ``backend='local'``
    uses ``fast-flights`` on your machine (requires ``pip install flightgrab[local]``).
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        timeout: float = 45.0,
        backend: str = "api",
        booking_api_key: Optional[str] = None,
    ):
        self.api_url = get_api_url(api_url)
        self.timeout = timeout
        self.backend = backend if backend in ("api", "local") else "api"
        self.booking_api_key = booking_api_key or os.getenv("FLIGHTGRAB_BOOKING_API_KEY")

    def find_flights(
        self,
        origin: str,
        destination: str,
        date: Optional[str] = None,
        max_stops: Optional[int] = None,
        max_price: Optional[float] = None,
        airlines: Optional[List[str]] = None,
        departure_after: Optional[str] = None,
        departure_before: Optional[str] = None,
        nonstop_only: bool = False,
        limit: int = 100,
    ) -> List[Flight]:
        """
        List flights for a route from stored FlightGrab data.

        Args:
            origin: 3-letter IATA origin.
            destination: 3-letter IATA destination.
            date: Optional ``YYYY-MM-DD`` filter. If omitted, returns up to ``limit``
                rows across future dates (sorted by price then date).
            max_stops: Maximum number of stops (after fetch).
            max_price: Maximum price in USD.
            airlines: Only these airline names (case-insensitive substring match on stored name).
            departure_after / departure_before: ``HH:MM`` string compare on ``departure_time``.
            nonstop_only: If True, only nonstop flights.
            limit: Max rows from API (1–200).

        Returns:
            Flights sorted by price ascending.
        """
        if self.backend == "local":
            if not date:
                raise ValueError(
                    "backend='local' requires date=YYYY-MM-DD (live scrape is for a single departure day)."
                )
            from .local_search import find_flights_local

            flights = find_flights_local(
                origin, destination, date, limit=min(max(limit, 1), 200)
            )
        else:
            params: Dict[str, Any] = {
                "origin": origin.upper(),
                "destination": destination.upper(),
                "limit": min(max(limit, 1), 200),
            }
            if date:
                params["departure_date"] = date

            response = requests.get(
                f"{self.api_url}/api/route-flights",
                params=params,
                timeout=self.timeout,
            )
            if response.status_code == 404:
                return []
            if response.status_code != 200:
                raise FlightGrabError(f"API error {response.status_code}: {response.text[:500]}")

            payload = response.json()
            rows = payload.get("flights") or []
            flights = [Flight.from_api_row(r) for r in rows]

        if nonstop_only:
            flights = [f for f in flights if f.stops == 0]
        elif max_stops is not None:
            flights = [f for f in flights if f.stops <= max_stops]

        if max_price is not None:
            flights = [f for f in flights if f.price <= max_price]

        if airlines:
            want = [a.strip().lower() for a in airlines if a.strip()]
            flights = [f for f in flights if f.airline and f.airline.lower() in want]

        if departure_after:
            flights = [f for f in flights if (f.departure_time or "") >= departure_after]
        if departure_before:
            flights = [f for f in flights if (f.departure_time or "") <= departure_before]

        flights.sort(key=lambda f: (f.price, f.departure_date, f.departure_time))
        return flights

    def get_route_info(self, origin: str, destination: str, limit: int = 200) -> RouteStats:
        """Aggregate min/avg/max and cheapest airline for a route (API backend only)."""
        if self.backend == "local":
            raise ValueError(
                "get_route_info requires aggregated DB data — use backend='api', or call "
                "find_flights(..., date=YYYY-MM-DD) with backend='local' and compute stats yourself."
            )
        flights = self.find_flights(origin, destination, limit=limit)
        if not flights:
            return RouteStats(
                origin=origin.upper(),
                destination=destination.upper(),
                total_flights=0,
                min_price=0.0,
                avg_price=0.0,
                max_price=0.0,
                cheapest_airline="",
            )
        prices = [f.price for f in flights]
        cheapest = min(flights, key=lambda f: f.price)
        return RouteStats(
            origin=origin.upper(),
            destination=destination.upper(),
            total_flights=len(flights),
            min_price=min(prices),
            avg_price=sum(prices) / len(prices),
            max_price=max(prices),
            cheapest_airline=cheapest.airline or "",
        )

    def export_csv(self, flights: List[Flight], filename: str) -> None:
        if not flights:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                f.write("")
            return
        with open(filename, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(flights[0].to_dict().keys()))
            w.writeheader()
            for fl in flights:
                w.writerow(fl.to_dict())

    def export_json(self, flights: List[Flight], filename: str) -> None:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([x.to_dict() for x in flights], f, indent=2)

    def to_dataframe(self, flights: List[Flight]):
        try:
            import pandas as pd
        except ImportError as e:
            raise ImportError("Install pandas: pip install flightgrab[pandas] or pip install pandas") from e
        return pd.DataFrame([f.to_dict() for f in flights])

    def create_alert(
        self,
        origin: str,
        destination: str,
        max_price: float,
        email: str,
        token: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a price alert via the FlightGrab API (requires a signed-in API token).

        Set ``FLIGHTGRAB_API_TOKEN`` (Bearer JWT from ``/api/auth/signin``) or pass ``token``.
        """
        auth = token or os.getenv("FLIGHTGRAB_API_TOKEN")
        if not auth:
            raise FlightGrabAuthError(
                "Alerts require a Bearer token. Sign in via the app and set FLIGHTGRAB_API_TOKEN, "
                "or pass token= to create_alert()."
            )
        headers = {"Authorization": f"Bearer {auth.strip()}"}
        body: Dict[str, Any] = {
            "origin": origin.upper()[:3],
            "destination": destination.upper()[:3],
            "target_price": float(max_price),
            "email": email.strip(),
        }
        if user_id:
            body["user_id"] = user_id
        response = requests.post(
            f"{self.api_url}/api/alerts/subscribe",
            json=body,
            headers=headers,
            timeout=self.timeout,
        )
        if response.status_code not in (200, 201):
            raise FlightGrabError(f"Alert failed {response.status_code}: {response.text[:500]}")
        try:
            return response.json()
        except Exception:
            return {"ok": True, "raw": response.text}

    def resolve_booking_for_flight(self, flight: Flight):
        """Resolve booking URLs for a flight (uses ``FLIGHTGRAB_BOOKING_API_KEY`` when server enforces auth)."""
        from .booking import resolve_booking

        return resolve_booking(
            flight.origin,
            flight.destination,
            flight.departure_date,
            api_url=self.api_url,
            api_key=self.booking_api_key,
            timeout=self.timeout,
        )
