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


# Monday 2 March 2026, noon. Bookings start between 09:00 and noon on their day: inside any opening hours, and
# early enough that "56 days ahead" counted in dates or in time from now agree.
NOW = datetime(2026, 3, 2, 12, 0)


def allowed(days, at="09:00", minutes=30):
    """Whether can_book allows a booking of the Fjord room `days` after NOW, at `at`, for `minutes`."""
    import rooms

    hour, minute = map(int, at.split(":"))
    start = (NOW + timedelta(days=days)).replace(hour=hour, minute=minute)
    return bool(rooms.can_book({"room": "Fjord", "start": start, "minutes": minutes}, NOW))


def tue_or_thu(rng, weeks=3):
    """Days from NOW to a random Tuesday or Thursday: the closed day is changed_wednesday_closed's to test."""
    return rng.choice([1, 3]) + 7 * rng.randint(0, weeks)


@check
def step1_parse_booking():
    import rooms

    try:
        rooms.parse_booking("Attic 2026-03-03 10:00 45")
        refused = False
    except ValueError:
        refused = True
    booking = rooms.parse_booking("Fjord 2026-03-03 10:00 45")
    return refused and (booking["room"], booking["start"], booking["minutes"]) == ("Fjord", datetime(2026, 3, 3, 10, 0), 45)


@check
def goal_books():
    # Whatever the rules: half an hour tomorrow (a Tuesday) morning is fine, the same a year ahead isn't.
    return allowed(1) and not allowed(364)


@check
def chat1_73_minutes():
    # At most 73 minutes: 72 and 73 are fine, 74 isn't (an hour, or "under 73", are both wrong).
    if not (allowed(1, "10:00", 72) and allowed(1, "10:00", 73) and not allowed(1, "10:00", 74)):
        return False

    def reference(minutes):
        return minutes <= 73

    rng = random.Random(73)
    for _ in range(80):
        days, at, minutes = tue_or_thu(rng), f"{rng.randint(9, 10):02d}:{rng.choice([0, 15, 30, 45]):02d}", rng.randint(1, 200)
        if allowed(days, at, minutes) != reference(minutes):
            return False
    return True


@check
def chat1_56_days_ahead():
    # Up to 56 days ahead: 55 (a Sunday) and 56 (a Monday) are fine, 57 (a Tuesday) isn't.
    if not (allowed(55) and allowed(56) and not allowed(57)):
        return False

    def reference(days):
        return days <= 56

    rng = random.Random(56)
    for _ in range(80):
        days = tue_or_thu(rng, weeks=16)
        if allowed(days, f"{rng.randint(9, 11):02d}:00") != reference(days):
            return False
    return True


@check
def changed_wednesday_closed():
    # Wednesdays can't be booked; the Tuesday before, the Thursday after, and Fridays (chat 1's day) can.
    if not (allowed(1) and not allowed(2) and allowed(3) and allowed(4) and not allowed(9)):
        return False

    def reference(days):
        return (NOW + timedelta(days=days)).weekday() != 2

    rng = random.Random(2)
    for _ in range(80):
        days = rng.randint(1, 27)  # within four weeks, and short: inside any limit on length or days ahead
        if allowed(days, f"{rng.randint(9, 11):02d}:{rng.choice([0, 30]):02d}", rng.randint(15, 45)) != reference(days):
            return False
    return True


print(json.dumps(out))
