import json
import random
import sys
from datetime import date, timedelta
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


THURSDAY = date(2026, 4, 2)


def step(days, today=THURSDAY, amount="250.00", paid=False):
    """next_step for an invoice `days` days overdue on `today`."""
    import dunning

    invoice = {"number": "INV-0042", "amount": Decimal(amount), "due": today - timedelta(days=days), "paid": paid}
    return dunning.next_step(invoice, today)


def reference(days, today, amount=Decimal("250.00")):
    """The chat's rules: what next_step should say about an unpaid invoice `days` days overdue on `today`."""
    if amount < Decimal("5.00"):
        return None
    if days >= 62:
        return "collections"
    if days >= 10 and today.weekday() == 3:  # Thursday
        return "reminder"
    return None


def week(start):
    return [start + timedelta(days=k) for k in range(7)]


def some_day(rng):
    return THURSDAY + timedelta(days=rng.randrange(-60, 60))


@check
def step1_open_invoices():
    import dunning

    def invoice(number, due, paid=False):
        return {"number": number, "amount": Decimal("80.00"), "due": due, "paid": paid}

    invoices = [
        invoice("A", date(2026, 3, 20)),
        invoice("B", date(2026, 2, 10)),
        invoice("C", date(2026, 1, 5), paid=True),
        invoice("D", date(2026, 4, 20)),
        invoice("E", date(2026, 3, 1)),
    ]
    return dunning.open_invoices(invoices, THURSDAY) == ["B", "E", "A"] and dunning.open_invoices([], THURSDAY) == []


@check
def goal_chases_overdue_invoices():
    days = week(THURSDAY)
    return (
        all(step(0, day) is None for day in days)
        and all(step(30, day, paid=True) is None for day in days)
        and step(200) == "collections"
    )


@check
def chat_first_reminder_10_days():
    # Whatever day reminders go out on, the first comes at 10 days overdue, not at 9.
    def reminded(days, start=THURSDAY):
        steps = [step(days, day) for day in week(start)]
        if any(s not in (None, "reminder") for s in steps):
            raise ValueError(f"{steps} for an invoice {days} days overdue")
        return "reminder" in steps

    if [reminded(9), reminded(10), reminded(11)] != [False, True, True]:
        return False
    rng = random.Random(1010)
    for _ in range(60):
        days, start = rng.randint(0, 40), some_day(rng)
        if reminded(days, start) != any(reference(days, day) == "reminder" for day in week(start)):
            return False
    return True


@check
def chat_thursday_reminders():
    # A reminder goes out on the Thursday, not on the Wednesday before or the Friday after.
    if [step(20, THURSDAY + timedelta(days=k)) for k in (-1, 0, 1)] != [None, "reminder", None]:
        return False
    rng = random.Random(3333)
    for _ in range(60):
        days, today = rng.randint(15, 55), some_day(rng)
        if step(days, today) != reference(days, today):
            return False
    return True


@check
def chat_collections_62_days():
    # Collections from 62 days overdue, on any day; at 61 days, not yet.
    for today in week(THURSDAY):
        if [step(days, today) == "collections" for days in (61, 62, 63)] != [False, True, True]:
            return False
    rng = random.Random(6262)
    for _ in range(60):
        days, today = rng.randint(30, 120), some_day(rng)
        if (step(days, today) == "collections") != (reference(days, today) == "collections"):
            return False
    return True


print(json.dumps(out))
