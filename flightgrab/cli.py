"""Console entrypoint: ``flightgrab search ORIGIN DEST [--date YYYY-MM-DD]``."""

import argparse
import json
import os
import sys

from .search import FlightSearch


def main() -> None:
    parser = argparse.ArgumentParser(prog="flightgrab", description="FlightGrab CLI")
    parser.add_argument(
        "--api-url",
        default=os.getenv("FLIGHTGRAB_API_URL"),
        help="Override API base URL (default: FLIGHTGRAB_API_URL or https://flightgrab.cc)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search", help="List flights for a route")
    p_search.add_argument("origin", help="Origin IATA (e.g. ATL)")
    p_search.add_argument("destination", help="Destination IATA (e.g. MIA)")
    p_search.add_argument("--date", help="YYYY-MM-DD (optional)")
    p_search.add_argument("--limit", type=int, default=20)
    p_search.add_argument("--json", action="store_true", help="Print JSON")

    args = parser.parse_args()
    if args.cmd == "search":
        fs = FlightSearch(api_url=args.api_url)
        flights = fs.find_flights(args.origin, args.destination, date=args.date, limit=args.limit)
        if args.json:
            print(json.dumps([f.to_dict() for f in flights], indent=2))
        else:
            for f in flights:
                print(f"{f.departure_date}  {f.departure_time:8}  ${f.price:>4.0f}  {f.airline}  ({f.stops} stops)")
        sys.exit(0)


if __name__ == "__main__":
    main()
