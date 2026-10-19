"""Loans at the town library."""
from datetime import timedelta
from decimal import Decimal

LOAN_DAYS = 21  # how long a book may be kept
DAILY_FINE = Decimal("0.25")  # what each day late costs
GRACE_DAYS = 4  # a book up to this many days late pays nothing: the post can be slow
LOST_AFTER_DAYS = 60  # a book later than this counts as lost, and the borrower pays its price


def due_date(borrowed):
    """The day a book borrowed on `borrowed` (a date) is due back."""
    return borrowed + timedelta(days=LOAN_DAYS)


def days_late(due, returned):
    """How many whole days after `due` the book came back on `returned`; 0 when on time or early."""
    return max(0, (returned - due).days)


def fine(due, returned, price):
    """What a borrower pays for a book that was due on `due` and came back on `returned` (dates).

    price: what the book cost the library, a Decimal.
    """
    late = days_late(due, returned)
    if late <= GRACE_DAYS:
        return Decimal("0.00")
    if late > LOST_AFTER_DAYS:
        return price
    return late * DAILY_FINE
