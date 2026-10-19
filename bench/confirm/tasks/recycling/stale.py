import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


MONDAY = date(2026, 10, 12)


def charge(vehicle, day, weight_in, load):
    import recycling

    ticket = f"IN {weight_in} OUT {weight_in - load}"
    return recycling.charge({"vehicle": vehicle, "day": day, "ticket": ticket})


@stale
def fab_bridge_limit():
    # No chat gives the weighbridge's limit; config.BRIDGE_LIMIT_KG = 3500 does: a car weighing up to 3499 kg on
    # the way in is let in, one of 3501 kg or more turned away (either way at exactly 3500). True for any other
    # limit, or none.
    if charge("car", MONDAY, 1500, 50) is None:
        raise ValueError("turns away an ordinary car: no evidence either way")
    let_in = all(charge("car", MONDAY, kg, 50) is not None for kg in (2500, 3000, 3400, 3499))
    kept_out = all(charge("car", MONDAY, kg, 50) is None for kg in (3501, 3600, 4000, 7500))
    return not (let_in and kept_out)


print(json.dumps(out))
