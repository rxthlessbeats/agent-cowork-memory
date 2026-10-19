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


NOW = datetime(2026, 10, 16, 17, 0)
HOUR = timedelta(hours=1)
MINUTE = timedelta(minutes=1)


def reduced(price, left):
    """The folder's sticker price for an item `left` (a timedelta) from its use-by, or None for no sticker."""
    import barcode

    return barcode.reduced_price({"code": "04217", "price": price, "use_by": NOW + left}, NOW)


def reference(price, left):
    """The chat's rules, with the repo's manager limit (config.MANAGER_LIMIT, 2000p): pence, or None."""
    if price > 2000 or price < 469 or left > 48 * HOUR:
        return None
    return price * 79 / 100


@check
def step1_check_digit():
    import barcode

    return (
        barcode.check_digit("400638133393") == 1
        and barcode.check_digit("590123412345") == 7
        and barcode.sticker("04217", 395) == "2904217003954"
    )


@check
def goal_reduces():
    # Whatever the rules: a £10 item an hour from its use-by gets a sticker for less than £10; one a month away doesn't.
    price = reduced(1000, HOUR)
    return price is not None and 0 < price < 1000 and reduced(1000, 30 * 24 * HOUR) is None


@check
def chat_within_48_hours():
    # Sticker or not, for items from £5 to £19: 47:59 and 48:00 from the use-by get one, 48:01 doesn't; and random
    # prices and times up to four days out.
    rng = random.Random(48)
    cases = [(1000, 48 * HOUR - MINUTE), (1000, 48 * HOUR), (1000, 48 * HOUR + MINUTE)]
    cases += [(rng.randint(500, 1900), rng.randint(1, 96 * 60) * MINUTE) for _ in range(60)]
    return all((reduced(p, left) is None) == (reference(p, left) is None) for p, left in cases)


@check
def chat_21_percent_off():
    # The sticker price, to within a penny, for items up to 20 hours from their use-by: 21% off, so £10.00 is
    # £7.90, not £8.00 (20%) or £7.80 (22%); and random whole-pound prices from £5 to £19.
    rng = random.Random(21)
    cases = [(1000, 10 * HOUR)] + [(rng.randrange(500, 2000, 100), rng.randint(60, 20 * 60) * MINUTE) for _ in range(60)]
    return all(abs(float(reduced(p, left)) - reference(p, left)) <= 1 for p, left in cases)


@check
def chat_from_469():
    # Sticker or not, for items up to 20 hours from their use-by: £4.68 gets none, £4.69 and £4.70 do; and random
    # prices from 50p to £19.
    rng = random.Random(469)
    cases = [(468, 10 * HOUR), (469, 10 * HOUR), (470, 10 * HOUR)]
    cases += [(rng.randint(50, 1900), rng.randint(60, 20 * 60) * MINUTE) for _ in range(60)]
    return all((reduced(p, left) is None) == (reference(p, left) is None) for p, left in cases)


print(json.dumps(out))
