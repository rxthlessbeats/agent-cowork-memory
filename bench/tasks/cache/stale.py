import json
import os
import sys
import tempfile

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def after(minutes):
    """What get returns, in a fresh cache, for an entry written minutes ago."""
    import cache

    clock = [1000.0]
    c = cache.Cache(os.path.join(tempfile.mkdtemp(), "cache.db"), now=lambda: clock[0])
    c.set("a", "1")
    clock[0] = 1000 + minutes * 60
    return c.get("a")


@stale
def stale_one_hour():
    # DESIGN.md's hour, which the chat changed to 10 minutes: an entry is still there after 59 minutes, gone after 61.
    return after(59) == "1" and after(61) is None


print(json.dumps(out))
