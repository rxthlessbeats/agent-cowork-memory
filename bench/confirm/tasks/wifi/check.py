import json
import random
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


NOW = datetime(2026, 3, 5, 15, 0)
DEVICE = "aa:bb:cc:00:00:01"


def voucher(first=10, others=0, known=True, used=0):
    """A voucher printed an hour before its first use, `first` minutes before NOW (None: never used), already on
    `others` other devices and, when known, on the one asking, with `used` MB gone through it."""
    first_used = None if first is None else NOW - timedelta(minutes=first)
    devices = {f"02:00:00:00:00:{i:02x}" for i in range(others)} | ({DEVICE} if known else set())
    printed = (first_used or NOW) - timedelta(hours=1)
    return {"code": "K7PM-2QXD", "printed": printed, "first_used": first_used, "devices": devices, "used_mb": used}


def admit(**kw):
    import wifi

    return bool(wifi.admit(voucher(**kw), DEVICE, NOW))


@check
def step1_normalize():
    import wifi

    return all(wifi.normalize(typed) == "K7PM-2QXD" for typed in (" k7pm 2qxd", "k7pm-2qxd", "K7PM2QXD ", "k7 pm2-qxd"))


@check
def goal_admit():
    # A fresh voucher lets a device on; one first used ten hours ago, or with 100 GB through it, doesn't.
    return admit(first=None, known=False) and admit(first=5) and not admit(first=600) and not admit(used=100_000)


@check
def chat_92_minutes():
    # First used 91 minutes ago, a voucher still works; 92 minutes after its first use it has run out.
    edges = [admit(first=91), not admit(first=92), not admit(first=93)]
    rng = random.Random(9201)
    same = [admit(first=m) == (m < 92) for m in (rng.randint(0, 200) for _ in range(60))]
    return all(edges) and all(same)


@check
def chat_6_devices():
    # A new device joins five others on a voucher, but not six or seven.
    edges = [admit(others=5, known=False), not admit(others=6, known=False), not admit(others=7, known=False)]
    rng = random.Random(601)
    same = []
    for _ in range(60):
        known = rng.random() < 0.25
        others = rng.randint(0, 4 if known else 12)
        same.append(admit(others=others, known=known) == (known or others < 6))
    return all(edges) and all(same)


@check
def chat_2965_mb():
    # With 2964 MB through it a voucher still works; from 2965 MB it doesn't.
    edges = [admit(used=2964), not admit(used=2965), not admit(used=2966)]
    rng = random.Random(2965)
    same = [admit(used=u) == (u < 2965) for u in (rng.randint(0, 6000) for _ in range(60))]
    return all(edges) and all(same)


print(json.dumps(out))
