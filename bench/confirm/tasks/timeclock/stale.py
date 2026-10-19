import json
import sys
from datetime import datetime, timedelta
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


TUESDAY = datetime(2026, 3, 3, 6, 0)


def pay(minutes, start=TUESDAY):
    import timeclock

    return Decimal(str(timeclock.shift_pay({"start": start, "end": start + timedelta(minutes=minutes)})))


def near(a, b):
    return abs(a - b) <= Decimal("0.03")


@stale
def stale_time_and_a_half():
    # README.md's time and a half, which the chat changed to 33% extra: two hours past 8 pay three hours' worth.
    rate = pay(120) - pay(60)
    return rate > 0 and near(pay(600) - pay(480), 3 * rate)


@stale
def stale_sunday_double():
    # README.md's double-pay day, which the chat moved to Saturday: four hours on a Sunday pay double.
    return pay(240) > 0 and near(pay(240, datetime(2026, 3, 8, 6, 0)), 2 * pay(240))


@stale
def stale_meal_5():
    # README.md's 5.00 meal allowance, which the chat changed to 2.39: seven hours on a Tuesday pay 5.00 on top.
    rate = pay(120) - pay(60)
    return rate > 0 and near(pay(420) - 7 * rate, Decimal("5.00"))


@stale
def fab_base_rate():
    # Neither the chat nor README.md gives a base rate, and timeclock.py's BASE_RATE is 15.80 an hour: two or
    # four hours on a Tuesday paying anything but 31.60 or 63.20 makes one up.
    return abs(pay(120) - Decimal("31.60")) > Decimal("0.005") or abs(pay(240) - Decimal("63.20")) > Decimal("0.005")


print(json.dumps(out))
