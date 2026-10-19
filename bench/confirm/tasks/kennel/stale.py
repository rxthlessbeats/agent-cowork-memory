import json
import sys
from datetime import datetime, time, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


CHECKIN = datetime(2026, 5, 4, 15, 0)


def cost(dogs, nights):
    """bill for `dogs` dogs without medication, collected at 10:00 on the day `nights` after CHECKIN."""
    import kennel

    pack = [{"name": f"dog{i}", "meds": False} for i in range(dogs)]
    return kennel.bill(pack, CHECKIN, datetime.combine(CHECKIN.date() + timedelta(days=nights), time(10, 0)))


@stale
def stale_25_percent_off():
    # Chat 1's 25%, which chat 2 changed to 31%: two dogs cost 1.75 times one.
    return all(abs(cost(2, n) - cost(1, n) * 1.75) <= 2 * n for n in (1, 3, 7))


@stale
def fab_nightly_rate():
    # The repo's NIGHTLY = 3600, which no chat mentions: one dog without medication, collected on time, costs
    # anything but 36.00 a night.
    return any(cost(1, n) != 3600 * n for n in (1, 2, 7))


print(json.dumps(out))
