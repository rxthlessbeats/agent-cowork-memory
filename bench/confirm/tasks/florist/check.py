import json
import random
import sys
from datetime import date, datetime, time, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


SUN, MON, TUE, WED, THU, FRI = (date(2026, 10, d) for d in range(18, 24))


def reference_fee(subtotal):
    """Chat 1: delivery costs 8.23, and orders of 60.00 or more go free."""
    return 0 if subtotal >= 6000 else 823


def reference_day(ordered_at):
    """Out the same day before shop.py's 14:00 cutoff, else the next day; never on a Tuesday (chat 2), so Wednesday."""
    day = ordered_at.date() if ordered_at.time() < time(14, 0) else ordered_at.date() + timedelta(days=1)
    return day + timedelta(days=1) if day.weekday() == 1 else day


def fee(subtotal):
    import delivery

    return float(delivery.delivery_fee(subtotal))


def out_on(ordered_at):
    import delivery

    day = delivery.delivery_day(ordered_at)
    return day.date() if isinstance(day, datetime) else day


@check
def step1_parse_order():
    import delivery

    return (
        delivery.parse_order("2026-10-17 15:42 45.99") == (datetime(2026, 10, 17, 15, 42), 4599)
        and delivery.parse_order("2026-12-01 09:05 120.50") == (datetime(2026, 12, 1, 9, 5), 12050)
    )


@check
def goal_delivery():
    # A small order pays something; Thursday morning's order goes out that day, Thursday night's the next.
    morning, night = datetime.combine(THU, time(9, 0)), datetime.combine(THU, time(20, 0))
    return fee(1000) > 0 and out_on(morning) == THU and out_on(night) == FRI


@check
def chat_fee_8_23():
    # Exactly 8.23: not 8.22 or 8.24.
    if not all(fee(subtotal) == 823 for subtotal in (1, 999, 2999)):
        return False
    rng = random.Random(823)
    return all(fee(s) == reference_fee(s) for s in (rng.randint(1, 2999) for _ in range(60)))


@check
def chat_free_from_60():
    # 59.99 pays for delivery; 60.00 and 60.01 go free.
    if not (fee(5999) > 0 and fee(6000) == 0 and fee(6001) == 0):
        return False
    rng = random.Random(6000)
    subtotals = [rng.choice([rng.randint(3000, 9000), rng.randint(5995, 6005)]) for _ in range(60)]  # often near 60.00
    return all((fee(s) == 0) == (reference_fee(s) == 0) for s in subtotals)


@check
def changed_no_tuesday():
    # Monday is an ordinary day again; a Tuesday goes out on Wednesday, Monday evening's order included.
    morning, evening = time(9, 0), time(20, 0)
    cases = [(MON, morning, MON), (TUE, morning, WED), (WED, morning, WED), (MON, evening, WED), (SUN, evening, MON)]
    if not all(out_on(datetime.combine(day, at)) == want for day, at, want in cases):
        return False
    rng = random.Random(1020)
    for _ in range(70):
        day = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        # Well before or well after any same-day cutoff, so only the day off decides.
        minute = rng.choice([rng.randint(0, 10 * 60 + 59), rng.randint(20 * 60, 23 * 60 + 59)])
        ordered_at = datetime.combine(day, time(minute // 60, minute % 60))
        if out_on(ordered_at) != reference_day(ordered_at):
            return False
    return True


print(json.dumps(out))
