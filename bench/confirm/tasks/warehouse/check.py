import json
import random
import sys
from datetime import date, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TUESDAY = date(2026, 5, 5)
SUNDAY = date(2026, 5, 10)


def order(levels, today=TUESDAY):
    """reorder for SKUs with these units on hand, every one sold yesterday; a SKU ordered 0 counts as not ordered."""
    import warehouse

    stock = {sku: {"on_hand": units, "last_sold": today - timedelta(days=1)} for sku, units in levels.items()}
    return {sku: units for sku, units in warehouse.reorder(stock, today).items() if units}


@check
def step1_read_stock():
    import warehouse

    text = "sku,on_hand,last_sold\nBOLT-M6,1200,2026-04-30\nNUT-M6,0,2026-05-02\n"
    return warehouse.read_stock(text) == {
        "BOLT-M6": {"on_hand": 1200, "last_sold": date(2026, 4, 30)},
        "NUT-M6": {"on_hand": 0, "last_sold": date(2026, 5, 2)},
    }


@check
def goal_orders_what_ran_out():
    # Whatever the rules: on a weekday an empty shelf is reordered, and a SKU with stock to spare isn't.
    got = order({"EMPTY": 0, "PLENTY": 100000})
    return got.get("EMPTY", 0) > 0 and "PLENTY" not in got


def random_stocks(rng, low, high):
    """60 random stock lists of 1 to 5 SKUs, with units on hand from low to high."""
    return [{f"SKU-{i}": rng.randint(low, high) for i in range(rng.randint(1, 5))} for _ in range(60)]


@check
def chat1_reorder_at_68():
    # Which SKUs are ordered: those with 68 units or fewer. 67, 68 and 69, then random stock lists.
    stocks = [{"A": 67, "B": 68, "C": 69}] + random_stocks(random.Random(68), 0, 300)
    return all(set(order(levels)) == {sku for sku, n in levels.items() if n <= 68} for levels in stocks)


@check
def chat1_up_to_752():
    # How many: enough to bring each low SKU back up to exactly 752 (0 orders 752, 1 orders 751), then random
    # stock lists far below any reorder point.
    stocks = [{"A": 0, "B": 1, "C": 40}] + random_stocks(random.Random(752), 0, 40)
    return all(order(levels) == {sku: 752 - n for sku, n in levels.items()} for levels in stocks)


@check
def chat2_no_orders_on_sundays():
    # Nothing on a Sunday; any other day, the order a Tuesday gets. Saturday, Sunday and Monday, then random days.
    rng = random.Random(81)
    levels = {"EMPTY": 0, "LOW": 5}
    usual = order(levels)
    days = [SUNDAY - timedelta(days=1), SUNDAY, SUNDAY + timedelta(days=1)]
    days += [SUNDAY + timedelta(days=rng.randint(-200, 200)) for _ in range(60)]
    return bool(usual) and all(order(levels, day) == ({} if day.weekday() == 6 else usual) for day in days)


print(json.dumps(out))
