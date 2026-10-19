import json
import random
import sys
from datetime import date, datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


PRICES = {"sourdough": 475, "rye": 425, "seeded loaf": 450, "baguette": 300, "croissant": 175, "cinnamon bun": 325}


def order(pickup, placed=None, items=None, trade=False):
    """An order picked up at pickup, placed a day before unless placed says otherwise."""
    return {
        "customer": "Ana",
        "trade": trade,
        "items": items or {"sourdough": 1, "croissant": 2},
        "placed": placed or pickup - timedelta(days=1),
        "pickup": pickup,
    }


def some_day(rng):
    return date(2025, 1, 1) + timedelta(days=rng.randint(0, 1000))


@check
def step1_parse_items():
    import bakery

    return (
        bakery.parse_items("2 sourdough, 6 croissant") == {"sourdough": 2, "croissant": 6}
        and bakery.parse_items("2 sourdough, 1 cinnamon bun") == {"sourdough": 2, "cinnamon bun": 1}
        and bakery.parse_items("1 rye, 2 rye") == {"rye": 3}
    )


@check
def goal_takes_orders():
    import bakery

    pickup = datetime(2026, 10, 14, 11, 0)  # a Wednesday
    return (
        bool(bakery.accept(order(pickup, placed=pickup - timedelta(days=2))))
        and not bakery.accept(order(pickup, placed=pickup + timedelta(hours=1)))
        and bakery.total(order(pickup, items={"sourdough": 2, "croissant": 3})) == 2 * 475 + 3 * 175
    )


@check
def chat1_81_minutes_ahead():
    # Placed 80, 81 and 82 minutes before a Wednesday noon pickup, then random lead times up to five hours
    # before pickups from 11:00 to 15:00 on days that aren't Fridays.
    import bakery

    rng = random.Random(81)
    cases = [(datetime(2026, 10, 14, 12, 0), lead) for lead in (80, 81, 82)]
    while len(cases) < 63:
        day = some_day(rng)
        if day.weekday() != 4:
            cases.append((datetime(day.year, day.month, day.day, rng.randint(11, 15)), rng.randint(0, 300)))
    return all(
        bool(bakery.accept(order(pickup, placed=pickup - timedelta(minutes=lead)))) == (lead >= 81)
        for pickup, lead in cases
    )


@check
def chat1_no_friday_pickups():
    # Pickups on a Thursday, a Friday and a Saturday, then on random days, each placed the day before.
    import bakery

    rng = random.Random(4)
    thursday = datetime(2026, 10, 15, 12, 0)
    pickups = [thursday + timedelta(days=k) for k in (0, 1, 2)]
    for _ in range(60):
        day = some_day(rng)
        pickups.append(datetime(day.year, day.month, day.day, rng.randint(11, 15)))
    return all(bool(bakery.accept(order(pickup))) == (pickup.weekday() != 4) for pickup in pickups)


@check
def chat2_trade_12_percent_off():
    # A 25.00 order for trade (22.00, where 11% or 13% off would give 22.25 or 21.75) and not, then random orders.
    import bakery

    rng = random.Random(12)
    wednesday = datetime(2026, 10, 14, 12, 0)
    orders = [order(wednesday, items={"sourdough": 4, "baguette": 2}, trade=trade) for trade in (True, False)]
    for _ in range(60):
        names = rng.sample(sorted(PRICES), rng.randint(1, 4))
        items = {name: rng.randint(1, 30) for name in names}
        orders.append(order(wednesday, items=items, trade=rng.random() < 0.6))

    def expect(o):
        full = sum(PRICES[name] * n for name, n in o["items"].items())
        return full * 88 // 100 if o["trade"] else full  # every price is a multiple of 25 cents: 12% is exact

    return all(bakery.total(o) == expect(o) for o in orders)


print(json.dumps(out))
