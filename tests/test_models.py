from flightgrab.models import Flight
from flightgrab.utils import parse_duration_minutes


def test_parse_duration():
    assert parse_duration_minutes("5h 30m") == 330
    assert parse_duration_minutes("2h") == 120


def test_flight_from_api_row():
    row = {
        "origin": "ATL",
        "destination": "MIA",
        "date": "2026-04-15",
        "price": 99.0,
        "airline": "Delta",
        "stops": 0,
        "duration": "2h 15m",
        "departure_time": "08:00",
        "booking_url": "https://example.com",
    }
    f = Flight.from_api_row(row)
    assert f.departure_date == "2026-04-15"
    assert f.duration_minutes == 135
    assert f.is_nonstop
