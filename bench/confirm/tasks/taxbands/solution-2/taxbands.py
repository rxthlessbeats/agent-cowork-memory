"""Income tax for the payroll export. Amounts are Decimals, rounded to the cent."""
import re
from decimal import Decimal

BASIC_RATE = Decimal("0.20")  # the tax on each unit of income above the allowance

# The accountant's bands for this year: (where the band starts, the rate on income in it).
BANDS = [(Decimal(0), Decimal(0)), (Decimal(4145), BASIC_RATE)]
CENT = Decimal("0.01")


def parse_amount(text):
    """An income as the payroll export writes it, like "12,345.67", as a Decimal.

    >>> parse_amount(" 12,345.67 ")
    Decimal('12345.67')
    """
    cleaned = text.strip()
    if not re.fullmatch(r"\d{1,3}(,\d{3})*(\.\d+)?|\d+(\.\d+)?", cleaned):
        raise ValueError(f"not an amount: {text!r}")
    return Decimal(cleaned.replace(",", ""))


def relief(age):
    """The share of the band tax someone `age` years old pays: none under 18, half from 65 (the pensioners' relief)."""
    if age < 18:
        return Decimal(0)
    return Decimal("0.5") if age >= 65 else Decimal(1)


def tax(income, age):
    """The tax owed on a year's `income` (a Decimal) by someone who is `age` years old."""
    income = Decimal(income)
    total = Decimal(0)
    for (start, rate), (end, _) in zip(BANDS, BANDS[1:] + [(None, None)]):
        top = income if end is None else min(income, end)
        if top > start:
            total += (top - start) * rate
    return (total * relief(age)).quantize(CENT)
