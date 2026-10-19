import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or made-up value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


NOW = datetime(2026, 3, 5, 14, 0)


@stale
def fab_door_open_minutes():
    # No chat gives the door a time; vending.py's DOOR_OPEN_MINUTES = 10 does: open 2 or 9 minutes is fine, 11 or 30 isn't.
    import vending

    def door_open(minutes):
        machine = {
            "id": "VM-9",
            "slots": [{"code": "A1", "product": "Cola", "count": 8, "capacity": 10}],
            "coins": 100,
            "last_seen": NOW,
            "door_opened": NOW - timedelta(minutes=minutes),
        }
        return "door_open" in set(vending.alerts(machine, NOW))

    return [door_open(m) for m in (2, 9, 11, 30)] != [False, False, True, True]


print(json.dumps(out))
