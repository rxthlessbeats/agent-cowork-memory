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


MONDAY = "2026-06-01 18:30"
ADULT, CHILD = 700, 400  # prices.ADULT, prices.CHILD


def reference(session, people):
    """What book should return: the chats' rules (66 swimmers, chat 2's), and prices.CHILD_UNDER (16)."""
    friday = datetime.strptime(session["start"], "%Y-%m-%d %H:%M").weekday() == 4
    if session["booked"] + len(people) > 66 or (friday and any(p["age"] < 16 for p in people)):
        return None
    return sum((CHILD if p["age"] < 16 else ADULT) * (61 if p["member"] else 100) // 100 for p in people)


def person(age=30, member=False):
    return {"age": age, "member": member}


def book(people, booked=0, start=MONDAY):
    import pool

    return pool.book({"start": start, "booked": booked}, people)


@check
def step1_parse_start():
    import pool

    return pool.parse_start("2026-06-03 07:00") == datetime(2026, 6, 3, 7, 0) and pool.parse_start(
        "2026-12-31 21:30"
    ) == datetime(2026, 12, 31, 21, 30)


@check
def goal_book():
    one = book([person()])
    two = book([person(), person()])
    return one > 0 and two > one and book([person()], booked=500) is None


@check
def changed_capacity_66():
    def takes(booked, n):
        return book([person()] * n, booked) is not None

    # The boundary: 65 or 66 swimmers in all is fine, a 67th isn't, and neither is chat 1's 85th.
    if not (takes(64, 1) and takes(65, 1) and takes(64, 2) and not takes(66, 1) and not takes(65, 2) and not takes(84, 1)):
        return False
    rng = random.Random(66)
    for _ in range(60):
        booked = rng.choice([rng.randint(0, 90), rng.randint(58, 68)])
        n = rng.randint(1, 6)
        if takes(booked, n) != (reference({"start": MONDAY, "booked": booked}, [person()] * n) is not None):
            return False
    return True


@check
def chat1_member_39():
    def pays(group):
        return round(book(group))

    # 39% off: 427 for a member adult and 244 for a member child, not 434 and 248 (38%) or 420 and 240 (40%).
    if pays([person(30, True)]) != 427 or pays([person(8, True)]) != 244 or pays([person(30)]) != ADULT:
        return False
    rng = random.Random(39)
    for _ in range(60):
        # Plainly children or plainly adults, on a Monday.
        group = [person(rng.choice([rng.randint(3, 10), rng.randint(20, 80)]), rng.random() < 0.5) for _ in range(rng.randint(1, 6))]
        if pays(group) != reference({"start": MONDAY, "booked": 0}, group):
            return False
    return True


@check
def chat1_friday_adults():
    def takes(day, group):
        return book(group, start=f"{day} 18:30") is not None

    family = [person(40), person(8)]
    # The boundary: Thursday and Saturday take a child, Friday doesn't, though it still takes adults.
    if not (
        takes("2026-06-04", family)
        and not takes("2026-06-05", family)
        and takes("2026-06-06", family)
        and takes("2026-06-05", [person(40), person(35)])
    ):
        return False
    rng = random.Random(5)
    for _ in range(60):
        day = date(2026, 6, 1) + timedelta(days=rng.randint(0, 150))
        group = [person(rng.choice([rng.randint(2, 10), rng.randint(20, 80)]), rng.random() < 0.3) for _ in range(rng.randint(1, 4))]
        start = f"{day.isoformat()} 18:30"
        if takes(day.isoformat(), group) != (reference({"start": start, "booked": 0}, group) is not None):
            return False
    return True


print(json.dumps(out))
