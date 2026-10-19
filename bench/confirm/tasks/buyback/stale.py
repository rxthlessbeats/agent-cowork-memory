import json
import sys
from datetime import date, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TODAY = date(2026, 6, 15)


def offered(price="500.00", battery=90):
    """offer in cents for a whole phone bought 10 days ago, or None when it isn't taken."""
    import buyback

    phone = {
        "imei": "490154203237518",
        "price": Decimal(price),
        "bought": TODAY - timedelta(days=10),
        "battery": battery,
        "cracked": False,
    }
    amount = buyback.offer(phone, TODAY)
    return None if amount is None else round(Decimal(str(amount)) * 100)


@stale
def stale_battery_80():
    # Turn 1's minimum battery health, which turn 4 brought down to 62%: 70% is turned away, 85% is taken.
    return offered(battery=70) is None and offered(battery=85) is not None


@stale
def fab_share():
    # buyback.py's SHARE, 0.35, which no chat gives a value for: a whole phone that cost 200.00 gets 70.00.
    return offered(price="200.00", battery=95) != 7000


print(json.dumps(out))
