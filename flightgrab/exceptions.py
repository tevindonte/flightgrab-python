"""Errors raised by FlightGrab."""


class FlightGrabError(Exception):
    """Base error for the FlightGrab client."""


class FlightGrabProRequired(FlightGrabError):
    """Raised when a Pro-only feature is used without a license or dev override."""

    def __init__(self, message=None):
        super().__init__(
            message
            or "This feature requires FlightGrab Pro. Set FLIGHTGRAB_LICENSE_KEY, "
            "or FLIGHTGRAB_PRO=1 for local development. See https://flightgrab.cc"
        )


class FlightGrabAuthError(FlightGrabError):
    """Raised when an authenticated API call is missing credentials."""
