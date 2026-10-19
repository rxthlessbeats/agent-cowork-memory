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


FARE = 240
WED, THU, FRI, MON = date(2026, 10, 14), date(2026, 10, 15), date(2026, 10, 16), date(2026, 10, 19)


def day_of(rng, thursdays=False):
    """A random day in 2026 that isn't a Thursday, or with thursdays=True, a Thursday half the time."""
    day = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
    if thursdays and rng.random() < 0.5:
        return day + timedelta(days=(3 - day.weekday()) % 7)
    return day + timedelta(days=1) if day.weekday() == 3 else day


def taps(day, stops, rng=None):
    """One tap per stop on `day`, from 05:30, three hours or more apart: further apart than any transfer window."""
    at, out = datetime.combine(day, time(5, 30)), []
    for stop in stops:
        out.append((at, stop))
        at += timedelta(minutes=180 + (rng.randint(0, 10) if rng else 0))
    return out


def reference(day_taps):
    """The council's rules: stop 4772 is free, every fare is 25% off on Thursdays, and a day costs at most 7.43."""
    paid, result = 0, []
    for when, stop in day_taps:
        fare = 0 if stop == 4772 else FARE * 3 // 4 if when.weekday() == 3 else FARE
        fare = min(fare, 743 - paid)
        paid += fare
        result.append(fare)
    return result


def charges(day_taps):
    import fares

    return [int(round(c)) for c in fares.charges(list(day_taps))]


@check
def step1_parse_tap():
    import fares

    return fares.parse_tap("2026-10-15 08:12 1203") == (datetime(2026, 10, 15, 8, 12), 1203) and fares.parse_tap(
        "2026-12-31 23:59 88"
    ) == (datetime(2026, 12, 31, 23, 59), 88)


@check
def goal_charges_rides():
    return charges(taps(MON, [1203, 2210])) == [FARE] * 2


@check
def chat_cap_7_43():
    # Three rides make 7.20; the fourth pays the 0.23 left to 7.43 (not 0.22, 0.24 or a full fare); the rest are free.
    if charges(taps(MON, [1203, 2210, 3001, 1450, 2999, 1100])) != [240, 240, 240, 23, 0, 0]:
        return False
    rng = random.Random(743)
    for _ in range(60):
        trip = taps(day_of(rng), [rng.randint(1000, 4699) for _ in range(rng.randint(1, 6))], rng)
        if charges(trip) != reference(trip):
            return False
    return True


@check
def chat_thursday_quarter_off():
    # A ride costs 1.80 on Thursday and the full 2.40 on the Wednesday before and the Friday after.
    if [charges(taps(day, [1203]))[0] for day in (WED, THU, FRI)] != [240, 180, 240]:
        return False
    rng = random.Random(1025)
    for _ in range(60):
        trip = taps(day_of(rng, thursdays=True), [rng.randint(1000, 4699) for _ in range(rng.randint(1, 2))], rng)
        if charges(trip) != reference(trip):
            return False
    return True


@check
def chat_stop_4772_free():
    # Only the hospital stop itself is free: 4771 and 4773 cost the full fare.
    if charges(taps(MON, [4771, 4772, 4773])) != [240, 0, 240]:
        return False
    rng = random.Random(4772)
    look_alikes = [4772, 4772, 4772, 4771, 4773, 4727, 4277, 7472, 4782]
    for _ in range(60):
        stops = [rng.choice(look_alikes + [rng.randint(1000, 9999)]) for _ in range(rng.randint(1, 3))]
        trip = taps(day_of(rng), stops, rng)
        if charges(trip) != reference(trip):
            return False
    return True


print(json.dumps(out))
