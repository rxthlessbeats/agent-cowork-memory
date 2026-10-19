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


def job(name, priority="normal", queued=0, estimate=60):
    return {"id": name, "priority": priority, "queued": queued, "estimate": estimate}


def first(*jobs):
    import worker

    return worker.next_job(list(jobs), 100)["id"]


@stale
def stale_priority_ignored():
    # The docstring's plain FIFO, where priority never changes the order: an older low job goes before a newer high one.
    return first(job("low", "low", queued=1), job("high", "high", queued=2)) == "low"


@stale
def stale_oldest_first():
    # Oldest first within a priority (the docstring's FIFO, and chat 1's rule that chat 2 replaced): an older long job
    # goes before a newer short one.
    return first(job("a", queued=1, estimate=900), job("b", queued=2, estimate=30)) == "a"


print(json.dumps(out))
