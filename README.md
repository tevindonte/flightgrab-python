# FlightGrab (Python)

Client library for **[FlightGrab](https://flightgrab.cc)** flight deals: search, export to CSV/JSON, optional pandas, and (Pro-gated) browser booking links. **Prices and itineraries come from [Google Flights](https://www.google.com/travel/flights)**–style data (see **Data source** below)—FlightGrab is not affiliated with Google.

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

## Data source (Google Flights)

- **`backend="api"` (default):** Results are served from the FlightGrab API, which stores and refreshes route/price data **sourced from Google Flights search** (same ecosystem users see on [Google Flights](https://www.google.com/travel/flights)).
- **`backend="local"`:** Uses a live scrape of Google Flights via **fast-flights** (see `pip install flightgrab[local]`).

FlightGrab and this package are **not** affiliated with Google. Use results for planning only; airlines and OTAs set final prices at checkout.

## Premium & API keys (same subscription as the website)

**PyPI is only the Python package.** There is no separate payment on PyPI. **FlightGrab Premium** is one subscription (Stripe), shared with [flightgrab.cc](https://flightgrab.cc): alerts, account features, and **API access for booking links**.

**After you subscribe** (upgrade on the site), activation is **automatic**: Stripe notifies the backend and your account is marked Premium—**no manual approval**, no extra “validation” step from you. Sign in, create an API key once in your account (Developer / keys UI or the documented `/api/keys` endpoints), set `FLIGHTGRAB_BOOKING_API_KEY` in your environment, and the client sends it on booking calls. The server then checks that your subscription is still active; you do not need to re-verify by hand each time.

**Server-enforced booking links:** when `FLIGHTGRAB_ENFORCE_BOOKING_AUTH=1`, the API expects `X-API-Key`. Keys are issued to signed-in Premium users and stored server-side (hashed). Operators can also allow static keys via `FLIGHTGRAB_BOOKING_API_KEYS` for testing or special cases.

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
