"""
Open the resolved booking URL in the default browser (Pro / dev gate).

  set FLIGHTGRAB_PRO=1
  # or set FLIGHTGRAB_LICENSE_KEY=... when you sell licenses
"""

import os

from flightgrab import FlightSearch, open_booking_link

if __name__ == "__main__":
    if not os.getenv("FLIGHTGRAB_PRO") and not os.getenv("FLIGHTGRAB_LICENSE_KEY"):
        print("Set FLIGHTGRAB_PRO=1 for local dev, or FLIGHTGRAB_LICENSE_KEY for Pro.")
        raise SystemExit(1)
    s = FlightSearch()
    flights = s.find_flights("ATL", "MIA", limit=1)
    if not flights:
        print("No flights returned.")
        raise SystemExit(1)
    url = open_booking_link(flights[0])
    print("Opened:", url)
