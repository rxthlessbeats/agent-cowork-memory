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


MONDAY = datetime(2026, 10, 12, 7, 0)
WEDNESDAY = datetime(2026, 10, 14, 7, 0)


def watering(moisture, now, last=None):
    """Minutes the folder runs a bed's drip."""
    import plants

    return plants.watering({"name": "tomatoes", "moisture": moisture, "last_watered": last}, now)


def reference(moisture, now, last=None):
    """The chat's rules, with the repo's gap between waterings (config.MIN_GAP_HOURS, 12)."""
    if now.weekday() == 3 or moisture >= 39 or (last is not None and now - last < timedelta(hours=12)):
        return 0
    return 46


def some_monday(rng):
    """A Monday in 2026-2028, between 07:00 and 21:00."""
    return MONDAY + timedelta(weeks=rng.randrange(104), minutes=rng.randrange(14 * 60))


def some_day(rng):
    """Any day in 2026-2028, between 07:00 and 21:00."""
    return MONDAY + timedelta(days=rng.randrange(730), minutes=rng.randrange(14 * 60))


@check
def step1_parse_reading():
    import plants

    return plants.parse_reading("tomatoes 2026-10-16T06:30 41.5%") == (
        "tomatoes",
        datetime(2026, 10, 16, 6, 30),
        41.5,
    ) and plants.parse_reading("herbs 2026-10-17T07:05 18") == ("herbs", datetime(2026, 10, 17, 7, 5), 18.0)


@check
def goal_waters_dry_beds():
    # Whatever the rules: a bone-dry bed that was never watered gets water on a Monday morning, a soaked one doesn't.
    return watering(5, MONDAY) > 0 and watering(95, MONDAY) == 0


@check
def chat_dry_under_39():
    # Watered or not, on Mondays: 38 and 38.9 watered, 39, 39.1 and 40 not; and random readings, the bed last
    # watered two days before or never.
    rng = random.Random(39)
    cases = [(m, MONDAY, None) for m in (38, 38.9, 39, 39.1, 40)]
    for _ in range(60):
        now = some_monday(rng)
        cases.append((rng.randint(0, 1000) / 10, now, rng.choice([None, now - timedelta(days=2)])))
    return all((watering(m, now, last) > 0) == (reference(m, now, last) > 0) for m, now, last in cases)


@check
def chat_46_minutes():
    # How long a dry bed's drip runs, to the minute (46, not 45 or 47): random dry readings on random Mondays.
    rng = random.Random(46)
    cases = [(10, MONDAY)] + [(rng.randint(0, 250) / 10, some_monday(rng)) for _ in range(60)]
    return all(watering(m, now) == reference(m, now) for m, now in cases)


@check
def chat_no_water_thursday():
    # Watered or not, for a dry bed: Wednesday and Friday watered, Thursday not; and random days.
    rng = random.Random(3)
    cases = [WEDNESDAY + timedelta(days=i) for i in range(3)] + [some_day(rng) for _ in range(70)]
    return all((watering(10, now) > 0) == (reference(10, now) > 0) for now in cases)


print(json.dumps(out))
