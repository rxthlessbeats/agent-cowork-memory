"""Planning for the catering company's events. Amounts are in cents."""

from rates import PER_GUEST


def servers(guests):
    """How many servers to send to an event for this many guests."""
    raise NotImplementedError


def arrival(start):
    """When the crew arrives for an event that starts at `start` (a datetime)."""
    raise NotImplementedError


def price(guests, start):
    """What the client pays for an event for this many guests that starts at `start` (a datetime), in cents."""
    raise NotImplementedError
