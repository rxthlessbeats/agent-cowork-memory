"""Loans at the town library."""
from datetime import timedelta
from decimal import Decimal

LOAN_DAYS = 21  # how long a book may be kept
DAILY_FINE = Decimal("0.25")  # what each day late costs


def due_date(borrowed):
    """The day a book borrowed on `borrowed` (a date) is due back."""
    return borrowed + timedelta(days=LOAN_DAYS)


def fine(due, returned, price):
    """What a borrower pays for a book that was due on `due` and came back on `returned` (dates).

    price: what the book cost the library, a Decimal.
    """
    raise NotImplementedError
