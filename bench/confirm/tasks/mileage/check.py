import json
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


WEDNESDAY = date(2026, 3, 11)


def settled(*trips, submitted=WEDNESDAY):
    """settle() on a claim of (miles, parking) trips, driven three days before it's submitted."""
    import mileage

    day = submitted - timedelta(days=3)
    claim = {"who": "test", "submitted": submitted, "trips": [{"day": day, "miles": m, "parking": Decimal(p)} for m, p in trips]}
    return mileage.settle(claim)


def amount(*trips):
    return Decimal(str(settled(*trips)["amount"]))


def day_of(x):
    return x.date() if isinstance(x, datetime) else x


def next_thursday(day):
    return day + timedelta(days=(3 - day.weekday()) % 7 or 7)


@check
def step1_parse_trip():
    import mileage

    a = mileage.parse_trip("2026-03-05 84 6.50")
    b = mileage.parse_trip("  2026-12-31   12 ")
    return (
        a["day"] == date(2026, 3, 5)
        and a["miles"] == 84
        and Decimal(str(a["parking"])) == Decimal("6.50")
        and b["day"] == date(2026, 12, 31)
        and b["miles"] == 12
        and Decimal(str(b["parking"])) == 0
    )


@check
def goal_settle():
    # A long trip pays more than a short one, parking adds to it, and the claim is paid within a fortnight.
    long_trip, short_trip, parked = amount((300, "0")), amount((100, "0")), amount((300, "5.00"))
    paid = day_of(settled((300, "0"))["paid_on"])
    return long_trip > short_trip > 0 and parked > long_trip and WEDNESDAY <= paid <= WEDNESDAY + timedelta(days=14)


@check
def changed_commute_37():
    # The first 37 miles of each trip aren't paid (the first plan said 57): 36 and 37 miles pay nothing, 38 pay for one.
    edges = [amount((36, "0")) == 0, amount((37, "0")) == 0, amount((38, "0")) > 0]
    rate = amount((137, "0")) / 100  # whatever a mile pays, 137 miles are paid for 100 of them
    rng = random.Random(3701)
    same = []
    for _ in range(60):
        miles = [rng.randint(0, 160) for _ in range(rng.randint(1, 3))]
        expected = rate * sum(max(0, m - 37) for m in miles)
        same.append(abs(amount(*[(m, "0") for m in miles]) - expected) < Decimal("0.01"))
    return all(edges) and rate > 0 and all(same)


@check
def chat_parking_up_to_7_96():
    # Parking is paid back up to 7.96 a trip: 7.95 and 7.96 in full, 7.97 as 7.96. Trips of 0 miles pay only parking.
    cap = Decimal("7.96")
    edges = [amount((0, p)) == min(Decimal(p), cap) for p in ("7.95", "7.96", "7.97")]
    rng = random.Random(796)
    same = []
    for _ in range(60):
        parking = [Decimal(rng.randint(0, 1600)) / 100 for _ in range(rng.randint(1, 3))]
        expected = sum(min(p, cap) for p in parking)
        same.append(abs(amount(*[(0, str(p)) for p in parking]) - expected) < Decimal("0.005"))
    return all(edges) and all(same)


@check
def chat_paid_next_thursday():
    def paid(day):
        return day_of(settled((50, "0"), submitted=day)["paid_on"])

    # Submitted on Wednesday 11 March 2026: paid the next day; on Thursday the 12th: a week later; on Friday the 13th: the 19th.
    edges = [
        paid(date(2026, 3, 11)) == date(2026, 3, 12),
        paid(date(2026, 3, 12)) == date(2026, 3, 19),
        paid(date(2026, 3, 13)) == date(2026, 3, 19),
    ]
    rng = random.Random(4403)
    same = []
    for _ in range(60):
        day = date(2026, 1, 1) + timedelta(days=rng.randint(0, 700))
        same.append(paid(day) == next_thursday(day))
    return all(edges) and all(same)


print(json.dumps(out))
