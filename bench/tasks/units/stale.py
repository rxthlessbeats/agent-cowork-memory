import json
import re
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def stale_rounds_up():
    # "1 mi is 1,60 km, not 1,61": the label rounds 1.609344 to 1,61 (or 1.61), overstating the size.
    import units

    return re.match(r"1[.,]61\b", units.label(1, "mi", "km")) is not None


print(json.dumps(out))
