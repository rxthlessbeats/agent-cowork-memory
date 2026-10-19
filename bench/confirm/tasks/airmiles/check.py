import json
import random
import sys
from datetime import date, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


WEDNESDAY = date(2026, 11, 4)


def reference(distance, cabin="economy", day=WEDNESDAY):
    """What earn should return: the chat's rules, and settings.MAX_MILES (15000) as the cap."""
    miles = max(distance, 911)
    if cabin == "business":
        miles = miles * 118 // 100
    if day.weekday() == 6:
        miles *= 2
    return min(miles, 15000)


def flight(distance, cabin="economy", day=WEDNESDAY):
    return {"date": day, "distance": distance, "cabin": cabin}


def earn(distance, cabin="economy", day=WEDNESDAY):
    import miles

    return round(miles.earn(flight(distance, cabin, day)))


def midweek(rng):
    """A random Tuesday to Friday: away from the double-miles day, old or new, and from a weekday off by one."""
    while True:
        day = date(2026, 1, 1) + timedelta(days=rng.randint(0, 364))
        if 1 <= day.weekday() <= 4:
            return day


@check
def step1_parse_flight():
    import miles

    return miles.parse_flight("2026-11-08 3451 business") == flight(3451, "business", date(2026, 11, 8)) and miles.parse_flight(
        "2027-01-29 120 economy"
    ) == flight(120, "economy", date(2027, 1, 29))


@check
def goal_earn():
    return earn(3000) == 3000 and earn(4000) == 4000 and earn(3000, "business") > 3000


@check
def chat_minimum_911():
    # The boundary: 910 miles flown earn 911, 911 earn 911, 912 earn 912; a short hop earns 911 too.
    if [earn(910), earn(911), earn(912), earn(150)] != [911, 911, 912, 911]:
        return False
    rng = random.Random(911)
    for _ in range(60):
        distance = rng.choice([rng.randint(50, 3000), rng.randint(890, 930)])
        day = midweek(rng)
        if earn(distance, "economy", day) != reference(distance, "economy", day):
            return False
    return True


@check
def chat_business_18():
    # 18% more: 1000 miles in business earn 1180, not 1170 (17%) or 1190 (19%). Flights long enough that no
    # minimum comes into it.
    if earn(1000, "business") != 1180 or earn(2500, "business") != 2950:
        return False
    rng = random.Random(18)
    for _ in range(60):
        distance = 50 * rng.randint(20, 100)
        day = midweek(rng)
        if earn(distance, "business", day) != reference(distance, "business", day):
            return False
    return True


@check
def chat_double_sunday():
    saturday, sunday, monday = date(2026, 11, 7), date(2026, 11, 8), date(2026, 11, 9)
    # The boundary: of Saturday, Sunday and Monday, only Sunday earns double.
    if [earn(2000, "economy", saturday), earn(2000, "economy", sunday), earn(2000, "economy", monday)] != [2000, 4000, 2000]:
        return False
    rng = random.Random(7)
    for _ in range(60):
        day = date(2026, 1, 1) + timedelta(days=rng.randint(0, 364))
        distance = rng.randint(1000, 5000)
        if earn(distance, "economy", day) != reference(distance, "economy", day):
            return False
    return True


print(json.dumps(out))
