import json
import random
import sys
from datetime import date, timedelta
from fractions import Fraction

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


SAT, SUN, MON, WED = date(2026, 10, 17), date(2026, 10, 18), date(2026, 10, 19), date(2026, 10, 21)


def clock(minute):
    minute %= 24 * 60
    return f"{minute // 60:02d}:{minute % 60:02d}"


def shift(name, role, minutes, start=17 * 60):
    """A shift `minutes` long that starts `start` minutes after midnight, past midnight if need be."""
    return {"name": name, "role": role, "start": clock(start), "end": clock(start + minutes), "trainee": False}


def length(s):
    """The check's own count of a shift's minutes."""
    (h1, m1), (h2, m2) = (map(int, s[k].split(":")) for k in ("start", "end"))
    return (h2 * 60 + m2 - h1 * 60 - m1) % (24 * 60)


def reference(pool, shifts, day):
    """The staff meeting's rules: a shift under 77 minutes gets nothing and doesn't count; the kitchen gets 38% and
    the floor the rest, each shared by minutes; on Sundays the floor gets the whole pool."""
    parts = {"floor": Fraction(1)} if day.weekday() == 6 else {"kitchen": Fraction(38, 100), "floor": Fraction(62, 100)}
    shares = {s["name"]: Fraction(0) for s in shifts}
    for role, part in parts.items():
        team = [s for s in shifts if s["role"] == role and length(s) >= 77]
        total = sum(length(s) for s in team)
        for s in team:
            shares[s["name"]] = pool * part * length(s) / total
    return shares


def shares(pool, shifts, day):
    import tips

    got = tips.share_out(pool, [dict(s) for s in shifts], day)
    return {s["name"]: float(got.get(s["name"], 0)) for s in shifts}


def close(got, want, cents=2):
    return all(abs(got[n] - float(want[n])) <= cents for n in want)


def crew(rng, cooks, servers, lo=200, hi=600):
    """Random shifts for `cooks` cooks and `servers` servers, each lo to hi minutes long."""
    staff = []
    for role, count in (("kitchen", cooks), ("floor", servers)):
        for i in range(count):
            staff.append(shift(f"{role[0].upper()}{i}", role, rng.randint(lo, hi), start=rng.randint(9 * 60, 20 * 60)))
    return staff


def weekday(rng):
    """A random Monday to Friday in 2026."""
    day = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
    while day.weekday() > 4:
        day += timedelta(days=1)
    return day


@check
def step1_minutes():
    import tips

    return (
        tips.minutes({"start": "17:00", "end": "23:15"}) == 375
        and tips.minutes({"start": "18:00", "end": "01:30"}) == 450
        and tips.minutes({"start": "09:05", "end": "09:50"}) == 45
    )


@check
def goal_shares_the_pool():
    got = shares(20000, [shift("K", "kitchen", 300), shift("F1", "floor", 300), shift("F2", "floor", 420)], WED)
    return 19990 <= sum(got.values()) <= 20003 and min(got.values()) >= 0 and got["F2"] > got["F1"] and got["K"] >= 1


@check
def chat_kitchen_38_percent():
    # One cook and one server: the cook gets 38.00 of 100.00, not 37.00 or 39.00.
    got = shares(10000, [shift("K", "kitchen", 300), shift("F", "floor", 300)], WED)
    if abs(got["K"] - 3800) > 2 or abs(got["F"] - 6200) > 2:
        return False
    rng = random.Random(3862)
    for _ in range(60):
        day, staff, pool = weekday(rng), crew(rng, rng.randint(1, 3), rng.randint(1, 4)), rng.randint(5000, 90000)
        if not close(shares(pool, staff, day), reference(pool, staff, day)):
            return False
    return True


@check
def chat_under_77_minutes_nothing():
    # 76 minutes gets nothing; 77 and 78 get a share.
    short = [shift(name, "floor", minutes) for name, minutes in (("A", 76), ("B", 77), ("C", 78))]
    got = shares(10000, [shift("K", "kitchen", 300), shift("F", "floor", 300)] + short, WED)
    if got["A"] >= 1 or got["B"] < 1 or got["C"] < 1:
        return False
    rng = random.Random(7677)
    for _ in range(60):
        day, pool = weekday(rng), rng.randint(5000, 90000)
        roles = [rng.choice(["kitchen", "floor"]) for _ in range(rng.randint(1, 5))]
        short = [shift(f"X{i}", role, rng.randint(40, 160)) for i, role in enumerate(roles)]
        staff = crew(rng, 1, 1) + short
        got, want = shares(pool, staff, day), reference(pool, staff, day)
        # Who is paid, and the whole pool paid out: a short shift's minutes don't dilute anyone's share.
        if {n for n in got if got[n] >= 1} != {n for n in want if want[n] > 0}:
            return False
        if abs(sum(got.values()) - pool) > 2 * len(staff):
            return False
    return True


@check
def chat_sunday_all_floor():
    staff = [shift("K", "kitchen", 300), shift("F1", "floor", 300), shift("F2", "floor", 450)]
    # Sunday: the cook gets nothing and the floor shares the whole pool by minutes; Saturday and Monday are ordinary.
    if not close(shares(10000, staff, SUN), {"K": 0, "F1": 4000, "F2": 6000}):
        return False
    if shares(10000, staff, SAT)["K"] < 1 or shares(10000, staff, MON)["K"] < 1:
        return False
    rng = random.Random(1018)
    for _ in range(70):
        day = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        if rng.random() < 0.5:
            day += timedelta(days=6 - day.weekday())
        staff, pool = crew(rng, rng.randint(1, 3), rng.randint(1, 4)), rng.randint(5000, 90000)
        got, want = shares(pool, staff, day), reference(pool, staff, day)
        if day.weekday() == 6 and not close(got, want):
            return False
        if day.weekday() != 6 and min(got.values()) < 1:
            return False
    return True


print(json.dumps(out))
