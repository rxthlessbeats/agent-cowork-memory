"""Loans at the town library."""
import calendar
from datetime import timedelta
from decimal import Decimal

LOAN_DAYS = 21  # how long a book may be kept
DAILY_FINE = Decimal("0.25")  # what each day late costs


def due_date(borrowed):
    """The day a book borrowed on `borrowed` (a date) is due back."""
    return borrowed + timedelta(days=LOAN_DAYS)


def days_late(due, returned):
    """Whole days late: days_late(date(2026, 5, 1), date(2026, 5, 4)) == 3, and 0 for a book back on time or early."""
    late = (returned - due).days
    return late if late > 0 else 0


def fine(due, returned, price):
    """What a borrower pays for a book that was due on `due` and came back on `returned` (dates).

    price: what the book cost the library, a Decimal. The board's rules: Tuesday is the amnesty day, when
    nothing returned pays anything; a book more than 60 days late is lost, and pays its price; up to 4 days
    late is free, and from 5 days late every day late costs the daily fine.
    """
    if calendar.day_name[returned.weekday()] == "Tuesday":
        return Decimal(0)
    late = days_late(due, returned)
    if late > 60:
        return Decimal(price)
    if late >= 5:
        return DAILY_FINE * late
    return Decimal(0)
