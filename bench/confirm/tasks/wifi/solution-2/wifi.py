"""The guest Wi-Fi portal. See README.md, though its voucher rules are out of date: a voucher runs out
92 minutes after its first use, works on up to 6 devices, and stops once 2965 MB have gone through it.

A voucher is a dict: {"code": "K7PM-2QXD", "printed": datetime, "first_used": datetime or None,
"devices": the set of device addresses already let on with it, "used_mb": the megabytes it has used}.
"""
import re
from datetime import datetime, timedelta

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


def normalize(code):
    """A voucher code in its printed form, however the guest typed it.

    >>> normalize(" k7pm 2qxd")
    'K7PM-2QXD'
    """
    bare = re.sub(r"[\s-]+", "", code).upper()
    return bare[:4] + "-" + bare[4:]


def why_not(voucher, device, now):
    """The reasons not to let device on with this voucher at now; none means let it on."""
    reasons = []
    if voucher["first_used"] is None:
        if (now - voucher["printed"]).total_seconds() > UNUSED_DAYS * 86400:
            reasons.append("unused too long")
    elif (now - voucher["first_used"]) / timedelta(minutes=1) >= 92:
        reasons.append("run out")
    if device not in voucher["devices"] and len(voucher["devices"]) + 1 > 6:
        reasons.append("too many devices")
    if voucher["used_mb"] >= 2965:
        reasons.append("data used up")
    return reasons


def admit(voucher, device, now):
    """Whether to let `device` online with this voucher at `now`."""
    return not why_not(voucher, device, now)
