"""The self-service jet wash bays: the bay controller's session log, and charging customers' cards.

The jet costs 15p for every started minute, up to 22 minutes; a session under 30 seconds is free;
members get config.MEMBER_DISCOUNT percent off.
"""

import math
from decimal import ROUND_HALF_UP, Decimal

import config


def sessions(path):
    """Every session in the bay controller's log at path, one parsed line each."""
    with open(path) as log:
        return [parse_log(line) for line in log if line.strip()]


def seconds_of(clock):
    hours, minutes, seconds = (int(part) for part in clock.split(":"))
    return hours * 3600 + minutes * 60 + seconds


def parse_log(line):
    """A log line as (bay, card, seconds the jet ran)."""
    bay, card, on, off = line.split()
    return bay, card, seconds_of(off) - seconds_of(on)


def charge(session):
    """What a session costs the customer's card, in pence."""
    seconds = session["seconds"]
    billed = 0 if seconds < 30 else min(math.ceil(seconds / 60), 22)
    pence = Decimal(15 * billed)
    if session.get("member"):
        pence *= Decimal(100 - config.MEMBER_DISCOUNT) / 100
    return int(pence.quantize(Decimal(1), rounding=ROUND_HALF_UP))
