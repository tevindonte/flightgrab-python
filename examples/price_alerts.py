"""
Price alerts require a JWT from FlightGrab sign-in.

  export FLIGHTGRAB_API_TOKEN="eyJ..."
"""

import os

from flightgrab import FlightSearch
from flightgrab.exceptions import FlightGrabAuthError

if __name__ == "__main__":
    if not os.getenv("FLIGHTGRAB_API_TOKEN"):
        print("Set FLIGHTGRAB_API_TOKEN (Bearer JWT from /api/auth/signin) to run this example.")
        raise SystemExit(1)
    try:
        s = FlightSearch()
        s.create_alert(
            origin="ATL",
            destination="MIA",
            max_price=150,
            email="you@example.com",
        )
        print("Alert created.")
    except FlightGrabAuthError as e:
        print(e)
