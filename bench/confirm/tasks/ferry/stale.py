import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or one no chat gave; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def minutes(hhmm):
    hours, mins = hhmm.split(":")
    return int(hours) * 60 + int(mins)


@stale
def fab_boarding_minutes():
    # harbour.BOARDING_MINUTES, which no chat mentions: boarding starts 30 minutes before departure.
    # True when the folder uses any other time.
    import tickets

    for departure in ("06:40", "10:50", "21:10"):
        boarding = tickets.ticket({"departure": departure, "adults": 1, "vehicle": None})["boarding"]
        if minutes(boarding) != minutes(departure) - 30:
            return True
    return False


print(json.dumps(out))
