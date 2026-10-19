import json
import re
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


def shown(*args):
    import times

    return times.fmt(datetime(*args, tzinfo=timezone.utc))


@stale
def stale_shown_in_utc():
    # The README's and settings.py's UTC: noon UTC on 1 July shows as 12:00, where Lisbon, on summer time, reads 13:00.
    return re.search(r"\b12:00\b", shown(2026, 7, 1, 12, 0))


@stale
def stale_year_first_date():
    # The README's "2026-12-31 23:00 UTC": the date year first, with dashes.
    return re.search(r"\b2026-12-31\b", shown(2026, 12, 31, 12, 0))


print(json.dumps(out))
