# FlightGrab (Python)

Client library for **[FlightGrab](https://flightgrab.cc)** flight deals: search stored routes, export to CSV/JSON, optional pandas, and (Pro-gated) browser booking links.

## Install

```bash
pip install flightgrab
```

Optional extras:

```bash
pip install flightgrab[pandas]   # DataFrame export
pip install flightgrab[local]    # live Google Flights scrape (fast-flights) for backend='local'
pip install flightgrab[dev]      # pytest, black, fast-flights for tests
```

### PyPI vs TestPyPI

Uploading to **TestPyPI** requires an API token created at [test.pypi.org](https://test.pypi.org) — a **pypi.org** token will return **403 Forbidden** on TestPyPI.

## Quick start

```python
from flightgrab import FlightSearch

search = FlightSearch()
flights = search.find_flights("ATL", "MIA", date="2026-04-15", limit=20)

for f in flights:
    print(f)   # Spirit: $89 (nonstop)
```

Point at a self-hosted API:

```python
import os
os.environ["FLIGHTGRAB_API_URL"] = "http://127.0.0.1:8000"
```

**Local scrape** (no FlightGrab DB): `FlightSearch(backend="local")` and `find_flights(..., date="YYYY-MM-DD")` — requires `pip install flightgrab[local]`.

**Server-enforced booking links:** set `FLIGHTGRAB_BOOKING_API_KEY` to a key listed in the API’s `FLIGHTGRAB_BOOKING_API_KEYS` when `FLIGHTGRAB_ENFORCE_BOOKING_AUTH=1` on the server.

## API surface (HTTP)

The client uses public endpoints on the FlightGrab backend:

- `GET /api/route-flights` — list flights for an origin/destination (optional `departure_date`, `limit`)
- `GET /api/book-redirect?format=json` — resolve a booking URL plus **`fallback_url`**, **`ttl_seconds`** (heuristic), and **`source`** (how the link was obtained). If an airline URL goes stale, call again or use the fallback (Google Flights search).
- `POST /api/alerts/subscribe` — price alerts (**requires** Bearer JWT from app sign-in)

## Pro: open booking in browser

Free tier includes search and export. Opening the system browser to a resolved booking URL is gated so you can sell a Pro license later:

- Set `FLIGHTGRAB_LICENSE_KEY`, or
- For local development: `FLIGHTGRAB_PRO=1`

```python
from flightgrab import FlightSearch, open_booking_link

# After setting FLIGHTGRAB_PRO=1 or a license key:
search = FlightSearch()
flights = search.find_flights("ATL", "MIA", date="2026-04-15", limit=1)
open_booking_link(flights[0])
```

`fetch_booking_url(...)` returns only the primary URL (no Pro). For full metadata:

```python
from flightgrab import resolve_booking
import time

r = resolve_booking("ATL", "MIA", "2026-04-15")
t0 = time.time()
# ... user waits ...
if r.is_expired(t0):
    r = resolve_booking("ATL", "MIA", "2026-04-15")  # fresh airline URL
# or open r.fallback_url (Google Flights search)
```

`open_booking_link(...)` returns a **`BookingResolution`** (opens browser; Pro-gated).

## CLI

```bash
flightgrab search ATL MIA --date 2026-04-15 --json
```

## Development

```bash
cd flightgrab-python
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Author

Tevin Parboosingh — [flightgrab.cc](https://flightgrab.cc)
