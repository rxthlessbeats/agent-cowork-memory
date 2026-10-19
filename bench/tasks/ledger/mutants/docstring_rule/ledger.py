"""Ledger amounts for the monthly report.

Amounts are exact Decimals. fmt() shows one the way the report prints it: rounded half up to whole
cents (see round_half_up), with a leading minus when negative, e.g. -1234.50.
"""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def round_half_up(amount):
    """The amount rounded to whole cents, ties away from zero: 2.345 -> 2.35, -2.345 -> -2.35."""
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def parse_amount(text):
    return Decimal(text)


def fmt(amount):
    return f"{round_half_up(amount):.2f}"
