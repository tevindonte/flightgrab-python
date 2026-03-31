# Quickstart

```bash
pip install flightgrab
```

```python
from flightgrab import FlightSearch

s = FlightSearch()
flights = s.find_flights("ATL", "MIA", date="2026-04-15")
for f in flights[:10]:
    print(f)
```

## Environment

| Variable | Purpose |
|----------|---------|
| `FLIGHTGRAB_API_URL` | API base (default `https://flightgrab.cc`) |
| `FLIGHTGRAB_API_TOKEN` | Bearer JWT for `create_alert` |
| `FLIGHTGRAB_LICENSE_KEY` or `FLIGHTGRAB_PRO` | Enable `open_booking_link` |

## CLI

```bash
flightgrab search ATL MIA --date 2026-04-15 --json
```
