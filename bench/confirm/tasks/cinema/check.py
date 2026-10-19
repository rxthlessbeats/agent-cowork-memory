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


BASE = {"standard": 1200, "3d": 1400, "imax": 1600}  # prices.BASE
START = datetime(2026, 11, 6, 20, 0)
EARLY = START - timedelta(days=2)


def reference(screen, kinds, now=EARLY):
    """What quote should return: the chats' rules, and prices.SENIOR_DISCOUNT (25) for seniors."""
    if now >= START + timedelta(minutes=13):
        return None
    off = {"adult": 0, "student": 40, "senior": 25}
    return sum(BASE[screen] * (100 - off[kind]) // 100 + 24 for kind in kinds)


def saved(price, screen, adults, students):
    """What turning `students` of the adult tickets into student ones saves, by `price` (quote or reference)."""
    return round(price(screen, ["adult"] * (adults + students)) - price(screen, ["adult"] * adults + ["student"] * students))


def quote(screen, kinds, now=EARLY):
    import tickets

    show = {"id": "T1", "film": "Test Film", "screen": screen, "start": START}
    return tickets.quote(show, kinds, now)


@check
def step1_parse_kinds():
    import tickets

    return (
        tickets.parse_kinds("2 adult, 1 student") == ["adult", "adult", "student"]
        and tickets.parse_kinds("1 senior") == ["senior"]
        and tickets.parse_kinds("3 adult") == ["adult", "adult", "adult"]
        and tickets.parse_kinds("") == []
    )


@check
def goal_quote():
    one = quote("imax", ["adult"])
    two = quote("imax", ["adult", "adult"])
    return one >= BASE["imax"] and two > one and quote("imax", ["adult"], START + timedelta(hours=3)) is None


@check
def chat1_student_40():
    # 40% off: a student saves 480 on a 1200 ticket, not 468 (39%) or 492 (41%).
    if saved(quote, "standard", 0, 1) != 480 or saved(quote, "imax", 1, 2) != 1280:
        return False
    rng = random.Random(40)
    for _ in range(60):
        screen = rng.choice(sorted(BASE))
        adults, students = rng.randint(0, 4), rng.randint(1, 5)
        if saved(quote, screen, adults, students) != saved(reference, screen, adults, students):
            return False
    return True


@check
def chat1_fee_24():
    def price(screen, n):
        return round(quote(screen, ["adult"] * n))

    # €0.24 a ticket: 1224 for one standard adult ticket, not 1223 or 1225.
    if price("standard", 1) != 1224 or price("imax", 2) != 2 * 1624:
        return False
    rng = random.Random(24)
    for _ in range(60):
        screen = rng.choice(sorted(BASE))
        n = rng.randint(1, 8)
        if price(screen, n) != reference(screen, ["adult"] * n):
            return False
    return True


@check
def chat2_close_13():
    def sells(seconds):
        return quote("standard", ["adult"], START + timedelta(seconds=seconds)) is not None

    # The boundary: a 20:00 show still sells at 20:12 and 20:12:59, not at 20:13 or 20:14.
    if not (sells(12 * 60) and sells(13 * 60 - 1) and not sells(13 * 60) and not sells(14 * 60)):
        return False
    rng = random.Random(13)
    for _ in range(60):
        seconds = rng.choice([rng.randint(-3 * 3600, 3600), rng.randint(11 * 60, 15 * 60)])
        if sells(seconds) != (reference("standard", ["adult"], START + timedelta(seconds=seconds)) is not None):
            return False
    return True


print(json.dumps(out))
