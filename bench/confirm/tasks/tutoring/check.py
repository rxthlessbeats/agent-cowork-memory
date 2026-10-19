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


MONDAY = date(2026, 5, 4)
WEDNESDAY = 2  # date.weekday()
NOT_WEDNESDAY = (0, 1, 3, 4, 5, 6)


def at(day, hour, minute=0):
    return datetime(day.year, day.month, day.day, hour, minute)


def session(student, tutor, start, minutes):
    return {"student": student, "tutor": tutor, "start": start, "minutes": minutes}


def books(sessions, new):
    """Whether the folder's can_book takes `new`, given `sessions`."""
    import tutoring

    return bool(tutoring.can_book(sessions, new))


def ends(s):
    return s["start"] + timedelta(minutes=s["minutes"])


def week_of(moment):
    day = moment.date()
    return day - timedelta(days=day.weekday())


def reference(sessions, new):
    """The centre's rules: what can_book should say."""
    if new["start"].weekday() == WEDNESDAY:
        return False
    if ends(new).date() != new["start"].date() or ends(new).time() > time(20, 0):
        return False
    week = week_of(new["start"])
    booked = sum(s["minutes"] for s in sessions if s["student"] == new["student"] and week_of(s["start"]) == week)
    if booked + new["minutes"] > 285:
        return False
    travel = timedelta(minutes=55)
    return not any(
        s["tutor"] == new["tutor"] and new["start"] < ends(s) + travel and s["start"] < ends(new) + travel
        for s in sessions
    )


@check
def step1_week_start():
    import tutoring

    return (
        tutoring.week_start(date(2026, 5, 6)) == date(2026, 5, 4)
        and tutoring.week_start(datetime(2026, 5, 10, 18, 30)) == date(2026, 5, 4)
        and tutoring.week_start(date(2026, 5, 4)) == date(2026, 5, 4)
        and tutoring.week_start(date(2026, 5, 11)) == date(2026, 5, 11)
        and tutoring.week_start(date(2026, 3, 1)) == date(2026, 2, 23)
    )


@check
def goal_books_and_refuses():
    lone = session("ana", "kim", at(MONDAY, 16), 45)
    clash = session("ben", "kim", at(MONDAY, 16), 45)
    return books([], lone) and not books([lone], clash)


@check
def chat1_no_wednesdays():
    # Tuesday and Thursday are open; Wednesday, the tutors' training day, is not.
    days = [MONDAY + timedelta(days=k) for k in (1, 2, 3)]
    if [books([], session("ana", "kim", at(day, 16), 45)) for day in days] != [True, False, True]:
        return False
    rng = random.Random(2222)
    for _ in range(60):
        day = MONDAY + timedelta(weeks=rng.randrange(20), days=rng.randrange(5))  # Monday to Friday
        new = session("ana", "kim", at(day, rng.randint(14, 18), rng.choice((0, 15, 30))), rng.randint(30, 60))
        if books([], new) != reference([], new):
            return False
    return True


@check
def chat1_285_minutes_a_week():
    # 240 minutes booked this week: 45 more makes 285, which is fine; 46 more is one minute too many.
    week = [
        session("ana", "t1", at(MONDAY, 10), 60),
        session("ana", "t2", at(MONDAY + timedelta(days=1), 10), 90),
        session("ana", "t3", at(MONDAY + timedelta(days=3), 10), 90),
    ]
    friday = MONDAY + timedelta(days=4)
    if [books(week, session("ana", "t4", at(friday, 13), m)) for m in (44, 45, 46)] != [True, True, False]:
        return False
    rng = random.Random(285)
    for _ in range(60):
        monday = MONDAY + timedelta(weeks=rng.randrange(20))
        booked = [
            session("ana", f"t{i}", at(monday + timedelta(days=d), 10), rng.randint(30, 75))
            for i, d in enumerate(rng.sample(NOT_WEDNESDAY, rng.randint(1, 4)))
        ]
        used = sum(s["minutes"] for s in booked)
        # Last week's sessions and another student's don't count towards this week.
        booked.append(session("ana", "t8", at(monday - timedelta(days=rng.randint(1, 2)), 10), rng.randint(60, 120)))
        booked.append(session("ben", "t9", at(monday + timedelta(days=rng.choice(NOT_WEDNESDAY)), 10), 120))
        minutes = max(15, 285 - used + rng.randint(-30, 15))
        new = session("ana", "tn", at(monday + timedelta(days=rng.choice(NOT_WEDNESDAY)), 13), minutes)
        if books(booked, new) != reference(booked, new):
            return False
    return True


@check
def chat2_55_minute_gap():
    # kim's first session ends at 16:00: the next can start at 16:55, not at 16:54.
    first = session("cat", "kim", at(MONDAY, 15), 60)
    if [books([first], session("dan", "kim", at(MONDAY, 16, m), 45)) for m in (54, 55, 56)] != [False, True, True]:
        return False
    rng = random.Random(5555)
    for _ in range(60):
        day = MONDAY + timedelta(weeks=rng.randrange(20), days=rng.choice((0, 1, 3, 4)))
        first = session("cat", "kim", at(day, 15), rng.randint(30, 60))
        minutes, gap = rng.randint(30, 60), timedelta(minutes=rng.randint(-20, 100))
        if rng.random() < 0.5:
            start = ends(first) + gap
        else:
            start = first["start"] - gap - timedelta(minutes=minutes)
        new = session("dan", "kim", start, minutes)
        other = session("eve", "lee", start, 45)  # another tutor at the same time doesn't matter
        if books([first, other], new) != reference([first, other], new):
            return False
    return True


print(json.dumps(out))
