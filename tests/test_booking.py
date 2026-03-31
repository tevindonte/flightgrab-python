import pytest

from flightgrab.booking import _pro_enabled, open_booking_link
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
