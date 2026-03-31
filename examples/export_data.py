"""Export search results to CSV / JSON."""

from flightgrab import FlightSearch

if __name__ == "__main__":
    s = FlightSearch()
    flights = s.find_flights("ATL", "MIA", limit=25)
    s.export_csv(flights, "sample_flights.csv")
    s.export_json(flights, "sample_flights.json")
    print("Wrote sample_flights.csv and sample_flights.json")
