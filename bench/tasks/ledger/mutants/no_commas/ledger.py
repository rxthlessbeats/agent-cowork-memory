"""Ledger amounts for the monthly report.

Amounts are exact Decimals. fmt() shows one the way the report prints it: banker's rounding (half to even) to
whole cents, negatives in parentheses, and no thousands separator: (1234.50).
"""

from decimal import ROUND_HALF_EVEN, Decimal

CENT = Decimal("0.01")


def parse_amount(text):
    return Decimal(text)


def fmt(amount):
    cents = amount.quantize(CENT, rounding=ROUND_HALF_EVEN)
    text = f"{abs(cents):.2f}"
    return f"({text})" if cents < 0 else text
