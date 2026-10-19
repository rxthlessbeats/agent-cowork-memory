import json
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


def ranks(scores):
    import leaderboard

    return {name: rank for rank, name, _ in leaderboard.ranking(scores)}


@stale
def stale_lowest_place():
    # Chat 1's rule, which chat 2 replaced with the average: tied players share their group's lowest place (1, 3, 3, 4).
    r = ranks({"ana": 30, "bo": 20, "cy": 20, "dee": 10})
    return r["bo"] == r["cy"] == 3


print(json.dumps(out))
