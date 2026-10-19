"""Chasing unpaid invoices. See README.md.

An invoice is a dict: number, amount (a Decimal), due (a date) and paid (True once it has been paid).
"""
from decimal import Decimal

MIN_AMOUNT = Decimal("5.00")  # invoices for less than this aren't worth chasing
FIRST_REMINDER = 10  # reminders start once an invoice is more than this many days overdue
REMINDER_DAY = 3  # Thursday, as date.weekday() counts: when the accounts team is in to take the calls
COLLECTIONS = 62  # days overdue, two full months: after that the agency recovers much less


def open_invoices(invoices, today):
    """The numbers of the unpaid invoices whose due date is before `today`, oldest due date first."""
    overdue = [i for i in invoices if not i["paid"] and i["due"] < today]
    return [i["number"] for i in sorted(overdue, key=lambda i: i["due"])]


def next_step(invoice, today):
    """What to do about `invoice` on `today` (a date): None, "reminder" or "collections".

    The rules in README.md are out of date; these are the current ones.
    """
    if invoice["paid"] or invoice["amount"] < MIN_AMOUNT:
        return None
    overdue = (today - invoice["due"]).days
    if overdue >= COLLECTIONS:
        return "collections"
    if overdue > FIRST_REMINDER and today.weekday() == REMINDER_DAY:
        return "reminder"
    return None
