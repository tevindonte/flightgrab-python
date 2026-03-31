from unittest.mock import MagicMock, patch

from flightgrab.search import FlightSearch


def test_find_flights_filters():
    payload = {
        "origin": "ATL",
        "destination": "MIA",
        "flights": [
            {
                "origin": "ATL",
                "destination": "MIA",
                "date": "2026-04-15",
                "price": 200.0,
                "airline": "Delta",
                "stops": 1,
                "duration": "2h",
                "departure_time": "10:00",
                "booking_url": "",
            },
            {
                "origin": "ATL",
                "destination": "MIA",
                "date": "2026-04-15",
                "price": 80.0,
                "airline": "Spirit",
                "stops": 0,
                "duration": "2h",
                "departure_time": "06:00",
                "booking_url": "",
            },
        ],
    }
    mock_get = MagicMock()
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = payload

    with patch("flightgrab.search.requests.get", mock_get):
        fs = FlightSearch(api_url="https://example.com")
        out = fs.find_flights("ATL", "MIA", nonstop_only=True, max_price=100)
        assert len(out) == 1
        assert out[0].airline == "Spirit"
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "/api/route-flights" in args[0]
