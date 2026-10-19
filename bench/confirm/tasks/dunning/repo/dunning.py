"""Chasing unpaid invoices. See README.md.

An invoice is a dict: number, amount (a Decimal), due (a date) and paid (True once it has been paid).
"""
from decimal import Decimal

MIN_AMOUNT = Decimal("5.00")  # invoices for less than this aren't worth chasing


def next_step(invoice, today):
    """What to do about `invoice` on `today` (a date): None, "reminder" or "collections". See README.md."""
    raise NotImplementedError
