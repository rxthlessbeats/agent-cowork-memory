"""Ledger amounts for the monthly report.

Amounts are exact Decimals. fmt() shows one the way the report prints it, through a float: whole cents, thousands
separated by commas, negatives in parentheses: (1,234.50).
"""

from decimal import Decimal


def parse_amount(text):
    return Decimal(text)


def fmt(amount):
    value = float(amount)
    text = f"{abs(value):,.2f}"
    return f"({text})" if value < 0 else text
