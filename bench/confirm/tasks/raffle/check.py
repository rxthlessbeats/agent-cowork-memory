import json
import random
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


DRAW_AT = datetime(2026, 3, 6, 20, 0)
DAY = timedelta(days=1)


def others(total):
    """Other buyers' tickets adding up to total, 50 each at most."""
    sold, n = {}, 0
    while total > 0:
        sold[f"Buyer {n}"] = min(50, total)
        total -= sold[f"Buyer {n}"]
        n += 1
    return sold


def can(count, held=0, sold_to_others=0, before=DAY):
    """Whether Ana Silva, holding `held` tickets, may buy `count` more `before` the draw, with others holding
    `sold_to_others` between them."""
    import raffle

    sold = others(sold_to_others)
    if held:
        sold["Ana Silva"] = held
    return bool(raffle.can_buy({"at": DRAW_AT, "sold": sold}, "Ana Silva", count, DRAW_AT - before))


@check
def step1_tickets_held():
    import raffle

    draw = {"at": DRAW_AT, "sold": {"Ana Silva": 12, "Ben Okafor": 3}}
    return (
        raffle.tickets_held(draw, "ana  SILVA") == 12
        and raffle.tickets_held(draw, "Ben Okafor") == 3
        and raffle.tickets_held(draw, "Cleo Ng") == 0
    )


@check
def goal_sells():
    # Whatever the limits: two tickets the day before a draw with none sold go through, two after it don't.
    return can(2) and not can(2, before=-timedelta(hours=1))


@check
def chat_58_per_buyer():
    # Nobody holds more than 58, counting what they have: with 50 held, 7 or 8 more go through and 9 don't; with
    # 58 held, not even one. (Capping each sale at 58, or 50 a head, both fail.)
    boundary = (
        can(7, held=50)
        and can(8, held=50)
        and not can(9, held=50)
        and not can(1, held=58)
        and can(58)
        and not can(59)
    )
    if not boundary:
        return False

    def reference(held, count):
        return held + count <= 58

    rng = random.Random(58)
    for _ in range(80):
        held, count = rng.randint(0, 58), rng.randint(1, 30)
        if can(count, held=held, sold_to_others=rng.randint(0, 600)) != reference(held, count):
            return False
    return True


@check
def chat_3580_total():
    # Never more than 3580 tickets for a draw: with 3579 sold, 1 more goes through and 2 don't; with 3580, none.
    boundary = (
        can(1, sold_to_others=3579)
        and not can(2, sold_to_others=3579)
        and not can(1, sold_to_others=3580)
        and can(2, sold_to_others=3578)
    )
    if not boundary:
        return False

    def reference(sold, count):
        return sold + count <= 3580

    rng = random.Random(3580)
    for _ in range(80):
        sold, count = rng.choice([rng.randint(3560, 3580), rng.randint(0, 3580)]), rng.randint(1, 10)
        if can(count, sold_to_others=sold) != reference(sold, count):
            return False
    return True


@check
def changed_65_minutes():
    # A sale has to be at least 65 minutes before the draw: 66 and 65 go through, 64 doesn't (nor does anything
    # under 65, where the first plan's 30 minutes would still sell).
    minute = timedelta(minutes=1)
    if not (can(1, before=66 * minute) and can(1, before=65 * minute) and not can(1, before=64 * minute)):
        return False

    def reference(minutes):
        return minutes >= 65

    rng = random.Random(65)
    for _ in range(80):
        minutes = rng.choice([rng.randint(1, 600), rng.randint(25, 75)])
        if can(rng.randint(1, 5), before=minutes * minute) != reference(minutes):
            return False
    return True


print(json.dumps(out))
