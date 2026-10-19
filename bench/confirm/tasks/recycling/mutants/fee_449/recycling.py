"""The recycling centre's gate: the weighbridge's tickets, and what each visit pays."""

import sys
from datetime import date

from config import BRIDGE_LIMIT_KG, SITE

FREE_KG = 78  # a car boot of garden waste: the council promised those stay free
FEE_PENCE = 449  # flat: the contractor bills us per load, not per kilo
VAN_DAY = 4  # Friday, as date.weekday() counts: the only day the trade skip has room for a van's load


def read_ticket(ticket):
    """The weight on the way in and the load left behind, in kg: read_ticket("IN 2140 OUT 1830") == (2140, 310)."""
    words = ticket.split()
    weight_in, weight_out = int(words[1]), int(words[3])
    return weight_in, weight_in - weight_out


def charge(visit):
    """What a visit pays at the gate, in pence (250 is £2.50), or None when the gate turns it away.

    visit: a dict with "vehicle" ("car" or "van"), "day" (a datetime.date) and "ticket", the
    weighbridge's ticket for the visit.
    """
    weight_in, load = read_ticket(visit["ticket"])
    if weight_in > BRIDGE_LIMIT_KG:
        return None
    if visit["vehicle"] == "van" and visit["day"].weekday() != VAN_DAY:
        return None
    return 0 if load <= FREE_KG else FEE_PENCE


if __name__ == "__main__":
    # python3 recycling.py car 2026-10-16 "IN 2140 OUT 1830"
    vehicle, day, ticket = sys.argv[1:4]
    pence = charge({"vehicle": vehicle, "day": date.fromisoformat(day), "ticket": ticket})
    print(f"{SITE}: " + ("turned away" if pence is None else f"£{pence / 100:.2f}"))
