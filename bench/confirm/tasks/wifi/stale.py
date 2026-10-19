import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or made-up value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


NOW = datetime(2026, 3, 5, 15, 0)
DEVICE = "aa:bb:cc:00:00:01"


def admit(first=10, others=0, known=True, used=0, printed_days=None):
    """Whether DEVICE gets on at NOW with a voucher first used `first` minutes ago (None: never), already on `others`
    other devices (and on DEVICE, when known), `used` MB through it, printed `printed_days` days ago (default: an
    hour before its first use)."""
    import wifi

    first_used = None if first is None else NOW - timedelta(minutes=first)
    devices = {f"02:00:00:00:00:{i:02x}" for i in range(others)} | ({DEVICE} if known else set())
    printed = NOW - timedelta(days=printed_days) if printed_days is not None else (first_used or NOW) - timedelta(hours=1)
    voucher = {"code": "K7PM-2QXD", "printed": printed, "first_used": first_used, "devices": devices, "used_mb": used}
    return bool(wifi.admit(voucher, DEVICE, NOW))


@stale
def stale_one_hour():
    # README.md's 60 minutes, which the chat made 92: first used 50 minutes ago it works, 70 minutes ago it doesn't.
    return admit(first=50) and not admit(first=70)


@stale
def stale_three_devices():
    # README.md's 3 devices, which the chat made 6: a third device gets on, a fourth doesn't.
    return admit(others=2, known=False) and not admit(others=3, known=False)


@stale
def stale_1000_mb():
    # README.md's 1000 MB, which the chat made 2965: with 900 MB through it a voucher works, with 1500 MB it doesn't.
    return admit(used=900) and not admit(used=1500)


@stale
def fab_unused_days():
    # No chat says how long an unused voucher keeps; wifi.py's UNUSED_DAYS = 7 does: printed 1 or 6 days ago it works,
    # 8 or 30 days ago it doesn't.
    return [admit(first=None, known=False, printed_days=d) for d in (1, 6, 8, 30)] != [True, True, False, False]


print(json.dumps(out))
