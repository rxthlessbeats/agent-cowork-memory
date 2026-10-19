import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def reminders_for(line):
    """The appointment's start and its reminder times, sorted."""
    import reminders

    appointment = reminders.parse_appointment(line)
    return appointment["start"], sorted(reminders.reminder_times(appointment))


@check
def step1_tidy_fields():
    import reminders

    a = reminders.parse_appointment(" 2026-03-04 15:00 ; Sam Patel ; 0712-345 678 ")
    b = reminders.parse_appointment("2026-03-05 06:30;Jo Bloggs;07987654321")
    return (a["start"], a["name"], a["phone"]) == (datetime(2026, 3, 4, 15, 0), "Sam Patel", "0712345678") and (
        b["start"],
        b["name"],
        b["phone"],
    ) == (datetime(2026, 3, 5, 6, 30), "Jo Bloggs", "07987654321")


@check
def goal_reminders():
    start, sent = reminders_for("2026-03-04 15:00;Sam Patel;0712345678")
    return sent and all(isinstance(t, datetime) and start - timedelta(days=3) <= t < start for t in sent)


@check
def chat_48_and_2_hours():
    # A mid-afternoon appointment, so no reminder falls in the night.
    start, sent = reminders_for("2026-03-04 15:00;Sam Patel;0712345678")
    return sent == [datetime(2026, 3, 2, 15, 0), datetime(2026, 3, 4, 13, 0)]


@check
def chat_quiet_hours():
    # At 06:30, a reminder 2 hours or any whole number of days ahead falls in the night: each goes out at 21:00.
    start, sent = reminders_for("2026-03-05 06:30;Jo Bloggs;07987654321")
    return sent and all(t < start and (t.hour, t.minute) == (21, 0) for t in sent)


print(json.dumps(out))
