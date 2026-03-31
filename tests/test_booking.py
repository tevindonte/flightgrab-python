import time
from unittest.mock import MagicMock, patch

import pytest

from flightgrab.booking import BookingResolution, _pro_enabled, open_booking_link, resolve_booking
from flightgrab.exceptions import FlightGrabProRequired
from flightgrab.models import Flight


def sample_flight():
    return Flight(
        price=100.0,
        airline="Test",
        origin="ATL",
        destination="MIA",
        departure_date="2026-04-15",
        departure_time="08:00",
        arrival_time="",
        duration_minutes=120,
        stops=0,
        booking_url="",
    )


def test_pro_enabled_env(monkeypatch):
    monkeypatch.delenv("FLIGHTGRAB_LICENSE_KEY", raising=False)
    monkeypatch.setenv("FLIGHTGRAB_PRO", "1")
    assert _pro_enabled() is True


def test_open_booking_requires_pro(monkeypatch):
    monkeypatch.delenv("FLIGHTGRAB_PRO", raising=False)
    monkeypatch.delenv("FLIGHTGRAB_LICENSE_KEY", raising=False)
    with pytest.raises(FlightGrabProRequired):
        open_booking_link(sample_flight())


def test_resolve_booking_parses_payload():
    mock_get = MagicMock()
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "url": "https://delta.com/book",
        "fallback_url": "https://www.google.com/travel/flights?q=a",
        "source": "airline_direct_cached",
        "ttl_seconds": 600,
        "refreshed_at": "2026-03-31T00:00:00Z",
        "hint": "retry after ttl",
    }
    with patch("flightgrab.booking.requests.get", mock_get):
        r = resolve_booking("ATL", "MIA", "2026-04-15", api_url="https://example.com")
    assert r.url == "https://delta.com/book"
    assert r.fallback_url.startswith("https://")
    assert r.source == "airline_direct_cached"
    assert r.ttl_seconds == 600


def test_booking_resolution_is_expired():
    r = BookingResolution(
        url="u",
        fallback_url="f",
        source="airline_direct_cached",
        ttl_seconds=600,
        refreshed_at="",
    )
    assert r.is_expired(time.time() - 700) is True
    assert r.is_expired(time.time() - 60) is False
