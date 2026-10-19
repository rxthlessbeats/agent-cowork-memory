"""The guest Wi-Fi portal. See README.md.

A voucher is a dict: {"code": "K7PM-2QXD", "printed": datetime, "first_used": datetime or None,
"devices": the set of device addresses already let on with it, "used_mb": the megabytes it has used}.
"""
from datetime import datetime, timedelta

UNUSED_DAYS = 7  # a voucher nobody has used is void this many days after it's printed
VOUCHER_TIME = timedelta(minutes=92)  # from its first use (README.md's 60 minutes is out of date)
MAX_DEVICES = 3  # as README.md says
DATA_MB = 2965  # README.md's 1000 MB is out of date

VOUCHERS = [
    {
        "code": "K7PM-2QXD",
        "printed": datetime(2026, 3, 2, 11, 5),
        "first_used": datetime(2026, 3, 2, 11, 9),
        "devices": {"3c:22:fb:10:4e:01"},
        "used_mb": 214,
    },
    {
        "code": "WD4Z-8HNA",
        "printed": datetime(2026, 3, 2, 12, 40),
        "first_used": None,
        "devices": set(),
        "used_mb": 0,
    },
]


def find(vouchers, code):
    """The voucher with this code, or None."""
    for voucher in vouchers:
        if voucher["code"] == code:
            return voucher
    return None


def normalize(code):
    """A voucher code as typed, in its printed form: " k7pm 2qxd" is "K7PM-2QXD"."""
    bare = "".join(code.split()).replace("-", "").upper()
    return f"{bare[:4]}-{bare[4:]}"


def admit(voucher, device, now):
    """Whether to let `device` online with this voucher at `now`."""
    first = voucher["first_used"]
    if first is None:
        if now - voucher["printed"] > timedelta(days=UNUSED_DAYS):
            return False
    elif now - first >= VOUCHER_TIME:
        return False
    if device not in voucher["devices"] and len(voucher["devices"]) >= MAX_DEVICES:
        return False
    return voucher["used_mb"] < DATA_MB
