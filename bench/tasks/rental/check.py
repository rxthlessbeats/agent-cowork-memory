import json
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


PICKUP = date(2026, 3, 2)


def cost(item, days):
    """price of renting item for this many days from PICKUP, rounded to cents, as a float."""
    import rental

    return round(float(rental.price(item, PICKUP, PICKUP + timedelta(days=days))), 2)


@check
def step1_return_before_pickup():
    try:
        cost("drill", -1)
    except ValueError:
        return cost("drill", 2) == 24
    return False


@check
def goal_long_rentals_cheaper():
    return cost("drill", 14) < 14 * 12 and cost("drill", 2) == 24


@check
def chat1_half_after_day_5():
    return cost("drill", 5) == 60 and cost("drill", 7) == 72 and cost("mixer", 10) == 262.50


@check
def chat1_same_day_half():
    return cost("drill", 0) == 6 and cost("mixer", 0) == 17.50


@check
def chat2_excavator_delivery():
    return cost("excavator", 1) == 335 and cost("excavator", 5) == 1295


print(json.dumps(out))
