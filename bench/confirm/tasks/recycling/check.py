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


MONDAY = date(2026, 10, 12)
THURSDAY = date(2026, 10, 15)


def charge(vehicle, day, weight_in, load):
    """What the folder charges a visit: pence, or None when it turns the visit away."""
    import recycling

    ticket = f"IN {weight_in} OUT {weight_in - load}"
    return recycling.charge({"vehicle": vehicle, "day": day, "ticket": ticket})


def reference(vehicle, day, weight_in, load):
    """The chat's rules, with the repo's weighbridge limit (config.BRIDGE_LIMIT_KG, 3500 kg)."""
    if weight_in > 3500 or (vehicle == "van" and day.weekday() != 4):
        return None
    return 0 if load <= 78 else 494


def some_day(rng):
    return date(2026, 1, 1) + timedelta(days=rng.randrange(730))


@check
def step1_read_ticket():
    import recycling

    return recycling.read_ticket("IN 2140 OUT 1830") == (2140, 310) and recycling.read_ticket("IN 980 OUT 980") == (980, 0)


@check
def goal_charges():
    # Whatever the rules: a car that leaves nothing pays nothing, and one that leaves 900 kg pays something.
    return charge("car", MONDAY, 1500, 0) == 0 and charge("car", MONDAY, 2400, 900) > 0


@check
def chat_free_up_to_78kg():
    # Free or not, for cars: 77 and 78 kg free, 79 kg not; and random loads on random days.
    rng = random.Random(78)
    cases = [(MONDAY, 77), (MONDAY, 78), (MONDAY, 79)]
    cases += [(some_day(rng), rng.randint(0, 300)) for _ in range(60)]
    return all((charge("car", d, 1300 + kg, kg) == 0) == (reference("car", d, 1300 + kg, kg) == 0) for d, kg in cases)


@check
def chat_flat_494():
    # What a paying car load pays, to the penny (£4.94, not £4.93 or £4.95): the lightest load the folder charges
    # for, whatever its free allowance, and the next; and random loads up to two tonnes on random days.
    first = next(kg for kg in range(1, 400) if charge("car", MONDAY, 1400 + kg, kg) != 0)
    rng = random.Random(494)
    edge = [charge("car", MONDAY, 1400 + kg, kg) == 494 for kg in (first, first + 1)]
    cases = [(some_day(rng), rng.randint(101, 2000)) for _ in range(60)]
    return all(edge) and all(charge("car", d, 1400 + kg, kg) == reference("car", d, 1400 + kg, kg) for d, kg in cases)


@check
def chat_vans_fridays_only():
    # Turned away or not, for vans: Thursday and Saturday turned away, Friday let in; and random days and loads.
    rng = random.Random(1564)
    cases = [(THURSDAY + timedelta(days=i), 300) for i in range(3)]
    cases += [(some_day(rng), rng.randint(0, 1000)) for _ in range(60)]
    return all(
        (charge("van", d, 2000 + kg, kg) is None) == (reference("van", d, 2000 + kg, kg) is None) for d, kg in cases
    )


print(json.dumps(out))
