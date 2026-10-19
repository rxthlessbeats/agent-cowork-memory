"""The recycling centre's gate: the weighbridge's tickets, and what each visit pays."""

import sys
from datetime import date

from config import SITE


def charge(visit):
    """What a visit pays at the gate, in pence (250 is £2.50), or None when the gate turns it away.

    visit: a dict with "vehicle" ("car" or "van"), "day" (a datetime.date) and "ticket", the
    weighbridge's ticket for the visit.
    """
    raise NotImplementedError


if __name__ == "__main__":
    # python3 recycling.py car 2026-10-16 "IN 2140 OUT 1830"
    vehicle, day, ticket = sys.argv[1:4]
    pence = charge({"vehicle": vehicle, "day": date.fromisoformat(day), "ticket": ticket})
    print(f"{SITE}: " + ("turned away" if pence is None else f"£{pence / 100:.2f}"))
