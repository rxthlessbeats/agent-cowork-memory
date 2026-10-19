"""Ledger amounts for the monthly report.

Amounts are exact Decimals. fmt() shows one the way the report prints it: rounded half up to whole cents, thousands
separated by commas, negatives in parentheses: (1,234.50).
"""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def parse_amount(text):
    return Decimal(text)


def fmt(amount):
    cents = amount.quantize(CENT, rounding=ROUND_HALF_UP)
    text = f"{abs(cents):,.2f}"
    return f"({text})" if cents < 0 else text
