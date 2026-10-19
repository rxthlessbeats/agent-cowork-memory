"""The courier's parcel tracking: the scans the drivers' handsets send, and refunds for late deliveries.

A delivery more than 21 minutes after its promised time is late, and gets a flat £3.18 back, unless
the parcel weighs over 20 kg or the claim came after config.CLAIM_DAYS.
"""

import re
from datetime import datetime, timedelta

import config

SCAN = re.compile(r"\s*(?P<parcel>\S+)\s+(?P<status>[A-Z_]+)\s+(?P<when>\S+)\s*")


def scans_for(scans, parcel):
    """The (parcel, status, when) scans for one parcel, oldest first."""
    found = []
    for item in scans:
        if item[0] == parcel:
            found.append(item)
    return sorted(found, key=lambda scan: scan[2])


def parse_scan(line):
    """A handset line as (parcel, status, when).

    >>> parse_scan("P-1042 DELIVERED 2026-10-16T14:05")
    ('P-1042', 'DELIVERED', datetime.datetime(2026, 10, 16, 14, 5))
    """
    match = SCAN.fullmatch(line)
    if not match:
        raise ValueError(f"not a scan: {line!r}")
    return match["parcel"], match["status"], datetime.fromisoformat(match["when"])


def minutes_late(delivery):
    return (delivery["delivered"] - delivery["promised"]) / timedelta(minutes=1)


def in_claim_window(delivery):
    claimed = delivery["claimed"]
    if isinstance(claimed, datetime):
        claimed = claimed.date()
    return claimed <= delivery["delivered"].date() + timedelta(days=config.CLAIM_DAYS)


def refund(delivery):
    """How much a delivery gets back, in pence, or 0 for nothing."""
    owed = minutes_late(delivery) > 21 and not delivery["kg"] > 20 and in_claim_window(delivery)
    return 318 if owed else 0

