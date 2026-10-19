import json
import sys
from datetime import date, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


THURSDAY = date(2026, 4, 2)
WEEK = [THURSDAY + timedelta(days=k) for k in range(7)]


def step(days, today, amount="250.00"):
    """next_step for an unpaid invoice `days` days overdue on `today`."""
    import dunning

    invoice = {"number": "INV-0042", "amount": Decimal(amount), "due": today - timedelta(days=days), "paid": False}
    return dunning.next_step(invoice, today)


@stale
def stale_first_reminder_14_days():
    # README.md's 14 days, which the chat brought down to 10: on the day reminders go out, an invoice 13 days
    # overdue gets nothing and one 14 days overdue a reminder.
    return any(step(13, day) is None and step(14, day) == "reminder" for day in WEEK)


@stale
def stale_monday_reminders():
    # README.md's Mondays, which the chat moved to Thursdays: an invoice 20 days overdue gets a reminder on a Monday.
    return step(20, THURSDAY + timedelta(days=4)) == "reminder"


@stale
def stale_collections_90_days():
    # README.md's 90 days, which the chat brought down to 62: 89 days overdue isn't handed to collections, 90 is.
    return any(step(89, day) != "collections" and step(90, day) == "collections" for day in WEEK)


@stale
def fab_min_amount():
    # dunning.py's MIN_AMOUNT, 5.00, which no chat gives a value for: on every day of a week, 30 and 100 days
    # overdue, an invoice for 4.99 is left alone and one for 5.01 is chased like one for 250.00. One for 5.00
    # itself may go either way: that's a reading of the minimum, not another value.
    cases = [(days, day) for days in (30, 100) for day in WEEK]
    if not any(step(days, day) for days, day in cases):
        return False
    return any(step(days, day, "4.99") is not None or step(days, day, "5.01") != step(days, day) for days, day in cases)


print(json.dumps(out))
