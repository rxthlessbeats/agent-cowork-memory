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


PRICES = {"water": 250, "cola": 390, "juice": 420, "beer": 560, "wine": 1450, "chocolate": 330, "nuts": 480, "crisps": 360}
SOLD = [item for item in PRICES if item != "water"]  # water is partly free, which no chat is about
WEDNESDAY = datetime(2026, 5, 6, 12, 0)
SUNDAY = datetime(2026, 5, 10)  # midnight, as Sunday starts


def owed(*events):
    """bill for a log of (when, "out" or "in", item) events."""
    import minibar

    return minibar.bill([f"{when:%Y-%m-%d %H:%M} {what} {item}" for when, what, item in events])


@check
def step1_parse():
    import minibar

    return (
        tuple(minibar.parse("2026-05-05 21:14 out cola")) == (datetime(2026, 5, 5, 21, 14), "out", "cola")
        and tuple(minibar.parse("2026-05-06 07:02 in chocolate")) == (datetime(2026, 5, 6, 7, 2), "in", "chocolate")
    )


@check
def goal_bills_what_was_taken():
    # Whatever the rules: an empty log owes nothing, and a bottle of wine never put back owes something.
    return owed() == 0 and owed((WEDNESDAY, "out", "wine")) > 0


@check
def chat_back_within_106_minutes():
    # Out and back after m minutes: free up to 106, then charged like an item never put back. At the edge, then random.
    rng = random.Random(106)
    kept = owed((WEDNESDAY, "out", "beer"))

    def back_after(m):
        return owed((WEDNESDAY, "out", "beer"), (WEDNESDAY + timedelta(minutes=m), "in", "beer"))

    gaps = [105, 106, 107] + [rng.randint(1, 360) for _ in range(60)]
    return all(back_after(m) == (0 if m <= 106 else kept) for m in gaps)


@check
def chat_077_restocking_fee():
    # On a weekday, every item never put back costs its price plus 0.77: none, one, two, then random baskets.
    rng = random.Random(77)

    def ok(items):
        got = owed(*[(WEDNESDAY + timedelta(minutes=i), "out", item) for i, item in enumerate(items)])
        return got == sum(PRICES[item] + 77 for item in items)

    baskets = [[], ["cola"], ["cola", "beer"]] + [[rng.choice(SOLD) for _ in range(rng.randint(1, 6))] for _ in range(60)]
    return all(ok(b) for b in baskets)


@check
def chat_no_fee_on_sundays():
    # Taken out on a Sunday: just the price. Any other day: what the same item costs on a Wednesday.
    # Saturday 23:59, Sunday 00:00, Sunday 23:59 and Monday 00:00, then random times.
    rng = random.Random(7)

    def ok(when, item):
        got = owed((when, "out", item))
        return got == PRICES[item] if when.weekday() == 6 else got == owed((WEDNESDAY, "out", item))

    edges = [SUNDAY - timedelta(minutes=1), SUNDAY, SUNDAY + timedelta(hours=23, minutes=59), SUNDAY + timedelta(days=1)]
    cases = [(when, "cola") for when in edges]
    cases += [(SUNDAY + timedelta(minutes=rng.randint(-4 * 1440, 10 * 1440)), rng.choice(SOLD)) for _ in range(60)]
    return all(ok(when, item) for when, item in cases)


print(json.dumps(out))
