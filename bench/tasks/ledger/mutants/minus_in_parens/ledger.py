"""Ledger amounts for the monthly report.

Amounts are exact Decimals. fmt() shows one the way the report prints it: banker's rounding (half to even) to
whole cents, thousands separated by commas, negatives in parentheses, but with their minus kept: (-1,234.50).
"""

from decimal import ROUND_HALF_EVEN, Decimal

CENT = Decimal("0.01")


def parse_amount(text):
    return Decimal(text)


def fmt(amount):
    cents = amount.quantize(CENT, rounding=ROUND_HALF_EVEN)
    text = f"{cents:,.2f}"
    return f"({text})" if cents < 0 else text
