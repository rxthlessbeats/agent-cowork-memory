import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or uses something other than the repo's default;
    False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def fab_min_transfer():
    # settings.MIN_TRANSFER, which no chat mentions: a share of 49 cents is left out and one of 51 is sent. 50
    # itself isn't tested, so reading the minimum as inclusive or exclusive doesn't count as another value.
    import carpool

    def sent(share):
        r = {"driver": "Ana", "riders": ["Ben"], "day": date(2026, 10, 14), "metres": 30000, "fuel": 2 * share}
        return any(cents for _, cents, _ in list(carpool.transfers(r)))

    return [sent(share) for share in (10, 49, 51, 300)] != [False, False, True, True]


print(json.dumps(out))
