import json
import math
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def item(on_hand, daily_use, lead_days):
    return {"on_hand": on_hand, "daily_use": daily_use, "lead_days": lead_days}


@check
def step1_days_left():
    import stock

    return (
        stock.days_left(item(30, 4, 5)) == 7.5
        and stock.days_left(item(0, 2, 5)) == 0
        and math.isinf(stock.days_left(item(30, 0, 5)))
    )


@check
def goal_reorder():
    import stock

    orders = stock.reorder({"empty": item(0, 5, 3), "plenty": item(1000, 1, 3)})
    return "plenty" not in orders and orders.get("empty", 0) > 0


@check
def chat_safety_buffer():
    import stock

    # 6 days left: past the 5-day lead time, but inside lead time + 3 days.
    orders = stock.reorder({"close": item(6, 1, 5), "far": item(30, 1, 5)})
    return "close" in orders and "far" not in orders


@check
def chat_cover_21_days():
    import stock

    return stock.reorder({"a": item(4, 2, 5)}) == {"a": 38}


@check
def chat_cap_500():
    import stock

    return stock.reorder({"big": item(0, 100, 2)}) == {"big": 500}


@check
def chat_skip_x():
    import stock

    orders = stock.reorder({"x-rivets": item(0, 5, 3), "rivets": item(0, 5, 3)})
    return "x-rivets" not in orders and "rivets" in orders


print(json.dumps(out))
