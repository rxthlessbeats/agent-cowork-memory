import json
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


MONDAY = datetime(2026, 3, 2)


def shift(who, day, hour, minutes, late=0):
    """who's shift on day (0 is Monday) from hour o'clock plus `late` minutes, lasting `minutes`."""
    begin = MONDAY + timedelta(days=day, hours=hour, minutes=late)
    return {"who": who, "start": begin, "end": begin + timedelta(minutes=minutes)}


def found(shifts, rates=None):
    """problems() as a set of (problem, who) pairs; anyone not in rates earns 15.00 an hour."""
    import roster

    rates = {**{s["who"]: Decimal("15.00") for s in shifts}, **(rates or {})}
    return {tuple(p) for p in roster.problems([dict(s) for s in shifts], rates)}


@check
def step1_week_hours():
    import roster

    got = roster.week_hours([shift("ana", 0, 8, 480), shift("ben", 0, 12, 270), shift("ana", 2, 9, 450)])
    return set(got) == {"ana", "ben"} and abs(float(got["ana"]) - 15.5) < 1e-9 and abs(float(got["ben"]) - 4.5) < 1e-9


@check
def goal_problems():
    # A calm week (two people, five 8-hour days) has none of these; 87.5 hours, two shifts back to back and a wage
    # bill in the tens of thousands each show up.
    calm = [shift(who, day, 9, 480) for who in ("ana", "ben") for day in range(5)]
    busy = [shift("ana", day, 6, 750) for day in range(7)] + [shift("ben", 0, 8, 240), shift("ben", 0, 12, 240)]
    wanted = {("too_many_hours", "ana"), ("short_rest", "ben"), ("over_budget", None)}
    kinds = {"too_many_hours", "short_rest", "over_budget"}
    return not {p for p, _ in found(calm)} & kinds and wanted <= found(busy, {"ana": Decimal("500.00")})


@check
def changed_cap_63_hours():
    def over(*lengths):
        return ("too_many_hours", "ana") in found([shift("ana", day, 8, h * 60) for day, h in enumerate(lengths)])

    # Seven days of 9 hours make 63, which is allowed, and so is 62; 64 isn't, though chat 1's 70 would allow it.
    edges = [not over(9, 9, 9, 9, 9, 9, 8), not over(9, 9, 9, 9, 9, 9, 9), over(9, 9, 9, 9, 9, 9, 10)]
    rng = random.Random(6301)
    same = []
    for _ in range(70):
        lengths = [rng.randint(14, 20) / 2 for _ in range(7)]
        same.append(over(*lengths) == (sum(lengths) > 63))
    return all(edges) and all(same)


@check
def chat1_rest_71_minutes():
    def short(gap):
        return ("short_rest", "ben") in found([shift("ben", 1, 7, 240), shift("ben", 1, 11, 240, late=gap)])

    # 71 minutes between the end of one shift and the start of the next is enough; 70 isn't.
    edges = [short(70), not short(71), not short(72)]
    rng = random.Random(7101)
    same = [short(gap) == (gap < 71) for gap in (rng.randint(0, 200) for _ in range(70))]
    return all(edges) and all(same)


@check
def chat1_budget_3975():
    # Three people on 40 hours and one on 38, all at 25.00, cost 3950.00; one more hour at 24.00, 25.00 or 26.00
    # makes 3974.00, 3975.00 or 3976.00, and only the last is over.
    team = [shift(who, day, 9, 480) for who in "abc" for day in range(5)]
    team += [shift("d", day, 9, 480 if day < 4 else 360) for day in range(5)]
    rates = {who: Decimal("25.00") for who in "abcd"}

    def over(extra):
        return ("over_budget", None) in found([*team, shift("e", 5, 9, 60)], {**rates, "e": Decimal(extra)})

    edges = [not over("24.00"), not over("25.00"), over("26.00")]
    rng = random.Random(3975)
    same = []
    for _ in range(60):
        shifts, pay, bill = [], {}, Decimal(0)
        for i in range(rng.randint(5, 6)):
            who = f"p{i}"
            pay[who] = Decimal(rng.randint(1400, 2400)) / 100
            for day in range(rng.randint(4, 6)):
                minutes = rng.randint(12, 20) * 30
                shifts.append(shift(who, day, 9, minutes))
                bill += pay[who] * minutes / 60
        same.append((("over_budget", None) in found(shifts, pay)) == (bill > 3975))
    return all(edges) and all(same)


print(json.dumps(out))
