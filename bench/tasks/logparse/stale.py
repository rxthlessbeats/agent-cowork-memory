import json
import sys
from datetime import datetime, timezone

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
def stale_helsinki_dst():
    # Helsinki time with DST, which the servers don't use: in January Helsinki is UTC+2, so 12:00 becomes 10:00 UTC
    # where the fixed UTC+3 gives 09:00. (In May the two agree, so the checks can't tell them apart.)
    import logparse

    record = logparse.parse_line("2024-01-15 12:00:03 INFO [billing] x")
    return record["time"] == datetime(2024, 1, 15, 10, 0, 3, tzinfo=timezone.utc)


print(json.dumps(out))
