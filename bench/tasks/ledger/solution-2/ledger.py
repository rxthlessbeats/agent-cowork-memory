"""Ledger amounts for the monthly report.

Amounts are exact Decimals. fmt() shows one the way the report prints it: rounded half up to whole
cents (see round_half_up), with a leading minus when negative, e.g. -1234.50.
"""

from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def round_half_up(amount):
    """The amount rounded to whole cents, ties away from zero: 2.345 -> 2.35, -2.345 -> -2.35."""
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def parse_amount(text):
    """The exact Decimal in text like "19.99" or "-3.5", not rounded."""
    return Decimal(text.strip())


def fmt(amount):
    """The amount as the report shows it (the docstring above is out of date): rounded to whole cents half to even,
    as the bank does, with thousands separated by commas and negatives in parentheses: -1234.5 -> (1,234.50)."""
    cents = int((amount * 100).to_integral_value(rounding=ROUND_HALF_EVEN))
    units, rest = divmod(abs(cents), 100)
    text = f"{units:,}.{rest:02d}"
    return f"({text})" if cents < 0 else text
