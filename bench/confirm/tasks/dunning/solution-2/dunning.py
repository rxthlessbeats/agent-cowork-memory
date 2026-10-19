"""Chasing unpaid invoices. See README.md, though its rules are out of date: STAGES has the current ones.

An invoice is a dict: number, amount (a Decimal), due (a date) and paid (True once it has been paid).
"""
import calendar
from decimal import Decimal

MIN_AMOUNT = Decimal("5.00")  # invoices for less than this aren't worth chasing

# Latest first: (days overdue from which the step applies, the step, the weekday it goes out on, or None for any).
STAGES = [
    (62, "collections", None),  # two full months: after that the agency recovers much less
    (10, "reminder", calendar.THURSDAY),  # one a week, when the accounts team is in to take the calls
]


def open_invoices(invoices, today):
    """The numbers of the unpaid invoices whose due date is before `today`, oldest due date first."""
    return [i["number"] for i in sorted(invoices, key=lambda i: i["due"]) if not i["paid"] and i["due"] < today]


def next_step(invoice, today):
    """What to do about `invoice` on `today` (a date): None, "reminder" or "collections"."""
    if invoice["paid"] or invoice["amount"] < MIN_AMOUNT:
        return None
    overdue = (today - invoice["due"]).days
    for start, action, weekday in STAGES:
        if overdue >= start:
            return action if weekday in (None, today.weekday()) else None
    return None
