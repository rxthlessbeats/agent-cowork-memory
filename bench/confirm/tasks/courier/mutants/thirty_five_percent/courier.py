"""The courier's parcel tracking: the scans the drivers' handsets send, and refunds for late deliveries."""

from datetime import datetime, timedelta

from config import CLAIM_DAYS

GRACE = timedelta(minutes=21)  # the app's 20-minute window, plus a minute for the driver
REFUND_PERCENT = 35  # of the fee
VAN_OVER_KG = 20  # heavier parcels go by van, and the van contract doesn't promise a time


def scans_for(scans, parcel):
    """The (parcel, status, when) scans for one parcel, oldest first."""
    found = []
    for item in scans:
        if item[0] == parcel:
            found.append(item)
    return sorted(found, key=lambda scan: scan[2])


def parse_scan(line):
    """A handset line as (parcel, status, when): "P-1042 DELIVERED 2026-10-16T14:05"."""
    parcel, status, when = line.split()
    return parcel, status, datetime.fromisoformat(when)


def refund(delivery):
    """How much a delivery gets back, in pence, or 0 for nothing."""
    if delivery["kg"] > VAN_OVER_KG:
        return 0
    if delivery["delivered"] - delivery["promised"] <= GRACE:
        return 0
    if (delivery["claimed"] - delivery["delivered"].date()).days > CLAIM_DAYS:
        return 0
    return delivery["fee"] * REFUND_PERCENT // 100
