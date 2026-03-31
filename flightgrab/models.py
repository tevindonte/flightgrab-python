"""Data models for FlightGrab."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Flight:
    """Represents one flight option returned by the API."""

    price: float
    airline: str
    origin: str
    destination: str
    departure_date: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    stops: int
    booking_url: str
    aircraft: Optional[str] = None

    def __str__(self) -> str:
        stops_text = "nonstop" if self.stops == 0 else f"{self.stops} stop{'s' if self.stops > 1 else ''}"
        return f"{self.airline}: ${self.price:.0f} ({stops_text})"

    def __repr__(self) -> str:
        return (
            f"Flight(price={self.price}, airline={self.airline!r}, "
            f"origin={self.origin!r}, destination={self.destination!r})"
        )

    @property
    def duration_hours(self) -> float:
        return self.duration_minutes / 60.0 if self.duration_minutes else 0.0

    @property
    def is_nonstop(self) -> bool:
        return self.stops == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "price": self.price,
            "airline": self.airline,
            "origin": self.origin,
            "destination": self.destination,
            "departure_date": self.departure_date,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "duration_minutes": self.duration_minutes,
            "duration_hours": self.duration_hours,
            "stops": self.stops,
            "is_nonstop": self.is_nonstop,
            "booking_url": self.booking_url,
            "aircraft": self.aircraft,
        }

    @classmethod
    def from_api_row(cls, row: Dict[str, Any]) -> "Flight":
        from .utils import parse_duration_minutes

        dep = row.get("date") or row.get("departure_date") or ""
        dur = row.get("duration") or ""
        return cls(
            price=float(row["price"]),
            airline=(row.get("airline") or "") or "",
            origin=row.get("origin") or "",
            destination=row.get("destination") or "",
            departure_date=dep if isinstance(dep, str) else "",
            departure_time=row.get("departure_time") or "",
            arrival_time=row.get("arrival_time") or "",
            duration_minutes=parse_duration_minutes(dur) if dur else int(row.get("duration_minutes") or 0),
            stops=int(row.get("stops") or row.get("num_stops") or 0),
            booking_url=row.get("booking_url") or "",
            aircraft=row.get("aircraft"),
        )


@dataclass
class RouteStats:
    """Simple aggregates for a route."""

    origin: str
    destination: str
    total_flights: int
    min_price: float
    avg_price: float
    max_price: float
    cheapest_airline: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origin": self.origin,
            "destination": self.destination,
            "total_flights": self.total_flights,
            "min_price": self.min_price,
            "avg_price": self.avg_price,
            "max_price": self.max_price,
            "cheapest_airline": self.cheapest_airline,
        }
