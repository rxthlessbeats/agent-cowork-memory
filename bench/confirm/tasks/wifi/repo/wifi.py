"""The guest Wi-Fi portal. See README.md.

A voucher is a dict: {"code": "K7PM-2QXD", "printed": datetime, "first_used": datetime or None,
"devices": the set of device addresses already let on with it, "used_mb": the megabytes it has used}.
"""
from datetime import datetime

UNUSED_DAYS = 7  # a voucher nobody has used is void this many days after it's printed

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


def admit(voucher, device, now):
    """Whether to let `device` online with this voucher at `now`."""
    return True
