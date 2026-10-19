"""The recycling centre's gate: the weighbridge's tickets, and what each visit pays.

Loads up to 78 kg go free; anything heavier pays a flat £4.94. Vans only come in on Fridays, and
nothing heavier than the weighbridge can weigh comes in at all.
"""

import calendar
import re
import sys
from datetime import date

import config

TICKET = re.compile(r"\s*IN\s+(\d+)\s+OUT\s+(\d+)\s*", re.IGNORECASE)


def read_ticket(ticket):
    """The weight on the way in and the load left behind, in kg, from a ticket like "IN 2140 OUT 1830"."""
    match = TICKET.fullmatch(ticket)
    if not match:
        raise ValueError(f"not a weighbridge ticket: {ticket!r}")
    weight_in, weight_out = (int(g) for g in match.groups())
    return weight_in, weight_in - weight_out


def turned_away(visit, weight_in):
    if weight_in > config.BRIDGE_LIMIT_KG:
        return True  # the weighbridge can't weigh it
    return visit["vehicle"] == "van" and visit["day"].weekday() != calendar.FRIDAY


def charge(visit):
    """What a visit pays at the gate, in pence (250 is £2.50), or None when the gate turns it away.

    visit: a dict with "vehicle" ("car" or "van"), "day" (a datetime.date) and "ticket", the
    weighbridge's ticket for the visit.
    """
    weight_in, load = read_ticket(visit["ticket"])
    if turned_away(visit, weight_in):
        return None
    return 494 if load > 78 else 0


if __name__ == "__main__":
    # python3 recycling.py car 2026-10-16 "IN 2140 OUT 1830"
    vehicle, day, ticket = sys.argv[1:4]
    pence = charge({"vehicle": vehicle, "day": date.fromisoformat(day), "ticket": ticket})
    print(f"{config.SITE}: " + ("turned away" if pence is None else f"£{pence / 100:.2f}"))
