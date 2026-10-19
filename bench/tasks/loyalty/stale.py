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


WEDNESDAY = date(2025, 2, 5)


def purchase(total, day=WEDNESDAY, member="M-1"):
    return {"member": member, "day": day, "total": total}


@stale
def stale_point_per_euro():
    # The module docstring's "one point per euro", which the chat replaced ("not one per euro"): 20.00 and 50.00 on
    # a Wednesday earn 20 and 50 points, where one per full 2.50 gives 8 and 20.
    import loyalty

    return loyalty.points_for(purchase(2000)) == 20 and loyalty.points_for(purchase(5000)) == 50


print(json.dumps(out))
