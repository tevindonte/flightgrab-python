"""Local backend tests (mock fast_flights)."""

from unittest.mock import MagicMock, patch

from flightgrab.search import FlightSearch


def test_find_flights_local_backend():
    fake_f = MagicMock()
    fake_f.price = "$199"
    fake_f.name = "TestAir"
    fake_f.departure = "08:00"
    fake_f.arrival = "11:00"
    fake_f.duration = "3h 0m"
    fake_f.stops = 0

    fake_result = MagicMock()
    fake_result.flights = [fake_f]

    with patch("fast_flights.get_flights", return_value=fake_result):
        s = FlightSearch(backend="local")
        out = s.find_flights("ATL", "MIA", date="2026-06-01", limit=10)

    assert len(out) == 1
    assert out[0].price == 199.0
    assert out[0].airline == "TestAir"


def test_local_requires_date():
    s = FlightSearch(backend="local")
    try:
        s.find_flights("ATL", "MIA", date=None)
    except ValueError as e:
        assert "date" in str(e).lower()
    else:
        raise AssertionError("expected ValueError")
