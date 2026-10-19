import json
import sys
from datetime import datetime

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
def stale_24_hours():
    # The docstring's reminder exactly 24 hours before: a 15:00 appointment gets one at 15:00 the day before.
    import reminders

    appointment = reminders.parse_appointment("2026-03-04 15:00;Sam Patel;0712345678")
    return datetime(2026, 3, 3, 15, 0) in reminders.reminder_times(appointment)


print(json.dumps(out))
