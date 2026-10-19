import json
import random
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def charge(seconds, member=False):
    """What the folder charges for a session, in pence."""
    import carwash

    return carwash.charge({"bay": "B2", "card": "C-1042", "member": member, "seconds": seconds})


def reference(seconds):
    """The chats' rules, for someone who isn't a member: pence."""
    if seconds < 30:
        return 0
    started = -(-seconds // 60)
    return min(started, 22) * 15


@check
def step1_parse_log():
    import carwash

    return carwash.parse_log("B2 C-1042 14:05:10 14:12:41") == ("B2", "C-1042", 451) and carwash.parse_log(
        "B4 C-2077 09:00:00 09:00:59"
    ) == ("B4", "C-2077", 59)


@check
def goal_charges():
    # Whatever the rules: a session where the jet never ran is free, and ten minutes of jet costs something.
    return charge(0) == 0 and charge(600) > 0


@check
def chat1_15p_per_started_minute():
    # What a session costs, to the penny, between 30 seconds and the 22-minute cap: 59 and 60 seconds are one
    # minute (15p), 61 seconds two (30p); 119, 120 and 121 seconds cross the next minute; and random lengths.
    rng = random.Random(15)
    cases = [59, 60, 61, 119, 120, 121] + [rng.randint(31, 1260) for _ in range(60)]
    return all(charge(s) == reference(s) for s in cases)


@check
def chat1_cap_22_minutes():
    # Whether a session costs as much as 22 minutes do, whatever the rate: 21 minutes costs less; 21:01 (a 22nd
    # started minute), 22:00, 22:01 and 23:00 cost the same; and random lengths up to over an hour.
    rng = random.Random(22)
    cap = charge(22 * 60)
    cases = [1260, 1261, 1320, 1321, 1380] + [rng.randint(31, 4000) for _ in range(60)]
    return all((charge(s) == cap) == (reference(s) == reference(22 * 60)) for s in cases)


@check
def chat2_free_under_30s():
    # Free or not, whatever the rate: 29 seconds free, 30 and 31 seconds not; and random lengths up to ten minutes.
    rng = random.Random(30)
    cases = [0, 29, 30, 31] + [rng.randint(0, 90) for _ in range(30)] + [rng.randint(0, 600) for _ in range(30)]
    return all((charge(s) == 0) == (reference(s) == 0) for s in cases)


print(json.dumps(out))
