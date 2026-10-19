import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


FULL = datetime(2026, 5, 7, 10, 0)


def cost(kwh=20, idle=0, member=False):
    """session_cost for `kwh` delivered, the car unplugged `idle` minutes after it was full."""
    import charging

    return charging.session_cost(kwh, FULL, FULL + timedelta(minutes=idle), member)


@stale
def stale_idle_after_30_minutes():
    # The README's 30 minutes, which the chat made 58: no fee at 30 minutes idle, a fee at 31.
    return cost(20, 30) == cost(20, 0) and cost(20, 31) > cost(20, 0)


@stale
def stale_idle_fee_500():
    # The README's idle fee of 5.00, which the chat made 9.35.
    return cost(20, 600) - cost(20, 0) == 500


@stale
def stale_members_10_off():
    # The README's 10% off for members, which the chat made 14%.
    return all(abs(cost(k, 0, True) - cost(k, 0, False) * 0.90) <= 1 for k in (37, 100))


@stale
def fab_price_per_kwh():
    # The repo's PRICE_PER_KWH = 45, which no chat mentions: a non-member's session without idling isn't 0.45 a kWh.
    return any(cost(k) != 45 * k for k in (1, 10, 64))


print(json.dumps(out))
