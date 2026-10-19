import json
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TUESDAY = datetime(2026, 3, 3, 6, 0)  # 3 March 2026 is a Tuesday; shifts start at 06:00 unless said otherwise


def shift(minutes, start=TUESDAY):
    return {"start": start, "end": start + timedelta(minutes=minutes)}


def pay(minutes, start=TUESDAY):
    """What shift_pay says a shift of this many minutes from start pays, as a Decimal."""
    import timeclock

    return Decimal(str(timeclock.shift_pay(shift(minutes, start))))


def near(a, b, cents=1):
    """a and b agree to within this many cents (and a half, for rounding)."""
    return abs(Decimal(str(a)) - Decimal(str(b))) <= Decimal("0.005") + Decimal(cents) / 100


def hourly():
    """An hour's pay at the base rate, whatever the base rate is: the second hour of a short Tuesday shift."""
    return pay(120) - pay(60)


@check
def step1_minutes():
    import timeclock

    try:
        timeclock.minutes(shift(-10))
        refused = False
    except ValueError:
        refused = True
    return refused and timeclock.minutes(shift(510)) == 510 and timeclock.minutes(shift(0)) == 0


@check
def goal_pays():
    # Whatever the extras: eight hours on a Tuesday pay more than four, and four pay something.
    return pay(480) > pay(240) > 0


@check
def chat_overtime_33_percent():
    # Past 8 hours, each minute pays 33% extra. At 15.80 an hour: the 480th minute pays 0.26, the 481st 0.35
    # (time and a half would be 0.40), and an hour of overtime 21.01 (time and a half 23.70, a third extra 21.07).
    # Tuesdays, so Saturday's double pay doesn't come in; every shift here gets the same meal allowance.
    rate, eight = hourly(), pay(480)
    boundary = (
        rate > 0
        and near(eight - pay(479), rate / 60, cents=2)
        and near(pay(481) - eight, rate * Decimal("1.33") / 60, cents=2)
        and near(pay(540) - eight, rate * Decimal("1.33"), cents=2)
    )
    if not boundary:
        return False

    def reference(minutes):
        return eight + (minutes - 480) * rate * Decimal("1.33") / 60

    rng = random.Random(33)
    for _ in range(80):
        minutes = rng.randint(480, 900)
        if not near(pay(minutes), reference(minutes), cents=2):
            return False
    return True


@check
def chat_saturday_double():
    # A Saturday shift pays twice the same shift on a Tuesday; Friday and Sunday (the README's old day) pay as
    # usual. Shifts of 6 hours at most, so no overtime or meal allowance comes in.
    four = pay(240)
    boundary = (
        four > 0
        and near(pay(240, datetime(2026, 3, 6, 6, 0)), four)
        and near(pay(240, datetime(2026, 3, 7, 6, 0)), 2 * four)
        and near(pay(240, datetime(2026, 3, 8, 6, 0)), four)
    )
    if not boundary:
        return False

    def reference(start, minutes):
        return (2 if start.weekday() == 5 else 1) * pay(minutes)

    rng = random.Random(5)
    for i in range(84):
        # Every day of four weeks three times over, at a random time between 06:00 and 12:00.
        start = datetime(2026, 3, 2, 6, 0) + timedelta(days=i % 28, minutes=rng.randint(0, 360))
        minutes = rng.randint(30, 360)
        if not near(pay(minutes, start), reference(start, minutes)):
            return False
    return True


@check
def chat_meal_2_39():
    # Shifts longer than 6 hours get a 2.39 meal allowance on top of their pay: 6 hours exactly gets none, a
    # minute more gets 2.39 (not the README's 5.00). Tuesday shifts under 8 hours: no overtime, no double pay.
    rate = hourly()

    def reference(minutes):
        return minutes * rate / 60 + (Decimal("2.39") if minutes > 360 else 0)

    boundary = rate > 0 and all(near(pay(m), reference(m)) for m in (359, 360, 361, 420))
    if not boundary:
        return False
    rng = random.Random(239)
    for _ in range(80):
        minutes = rng.choice([rng.randint(240, 479), rng.randint(350, 370)])
        if not near(pay(minutes), reference(minutes)):
            return False
    return True


print(json.dumps(out))
