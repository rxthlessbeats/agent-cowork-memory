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


MON, TUE, WED, THU = date(2026, 10, 19), date(2026, 10, 20), date(2026, 10, 21), date(2026, 10, 22)


def reference_setpoint(requested):
    """The chat: the heater never goes above 96 °C (README.md's 100 is out of date)."""
    return min(requested, 96)


def reference_end(start):
    """The chat: a session lasts 76 minutes (README.md's 90 is out of date)."""
    return start + timedelta(minutes=76)


def reference_open_midday(when):
    """The chat: closed on Wednesdays, and Mondays are normal days (README.md's Monday is out of date). Only for
    times in the middle of the day, when any opening hours have the door open."""
    return when.weekday() != 2


@check
def step1_parse_slot():
    import sauna

    return sauna.parse_slot("2026-10-21 18:45") == datetime(2026, 10, 21, 18, 45) and sauna.parse_slot(
        "2026-10-22 9:05"
    ) == datetime(2026, 10, 22, 9, 5)


@check
def goal_rules():
    import sauna

    start = datetime(2026, 10, 22, 15, 0)
    return (
        sauna.setpoint(80) == 80
        and sauna.session_end(start) > start
        and bool(sauna.is_open(start))
        and not sauna.is_open(datetime(2026, 10, 22, 3, 0))
    )


@check
def chat_heater_96():
    import sauna

    # 95 and 96 as asked; 97 goes no higher than 96.
    if [sauna.setpoint(t) for t in (95, 96, 97)] != [95, 96, 96]:
        return False
    rng = random.Random(9600)
    for _ in range(60):
        requested = rng.randint(60, 130)
        if sauna.setpoint(requested) != reference_setpoint(requested):
            return False
    return True


@check
def chat_session_76_minutes():
    import sauna

    # 76 minutes, not 75 or 77: 18:00 ends at 19:16; 23:30 ends at 00:46 the next day.
    if sauna.session_end(datetime(2026, 10, 22, 18, 0)) != datetime(2026, 10, 22, 19, 16):
        return False
    if sauna.session_end(datetime(2026, 10, 22, 23, 30)) != datetime(2026, 10, 23, 0, 46):
        return False
    rng = random.Random(7690)
    for _ in range(60):
        start = datetime(2026, 1, 1) + timedelta(days=rng.randrange(365), minutes=rng.randrange(24 * 60))
        if sauna.session_end(start) != reference_end(start):
            return False
    return True


@check
def chat_closed_wednesday():
    import sauna

    # Closed on Wednesday, open on the Tuesday before and the Thursday after, and open on Monday again.
    seen = [bool(sauna.is_open(datetime.combine(day, time(15, 0)))) for day in (MON, TUE, WED, THU)]
    if seen != [True, True, False, True]:
        return False
    rng = random.Random(2110)
    for _ in range(70):
        day = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        if rng.random() < 0.5:
            day += timedelta(days=(rng.choice([0, 2]) - day.weekday()) % 7)  # many Mondays and Wednesdays
        when = datetime.combine(day, time(rng.randint(12, 19), rng.randrange(60)))
        if bool(sauna.is_open(when)) != reference_open_midday(when):
            return False
    return True


print(json.dumps(out))
