"""Minimal example: search a route (requires network)."""

import os

# Point at production or a local FlightGrab instance:
# os.environ["FLIGHTGRAB_API_URL"] = "http://127.0.0.1:8000"

from flightgrab import FlightSearch

if __name__ == "__main__":
    search = FlightSearch()
    flights = search.find_flights("ATL", "MIA", date="2026-04-15", limit=10)
    for f in flights[:5]:
        print(f)
