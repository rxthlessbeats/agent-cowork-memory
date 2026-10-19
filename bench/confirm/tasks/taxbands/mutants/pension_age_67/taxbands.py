"""Income tax for the payroll export. Amounts are Decimals, rounded to the cent."""
from decimal import ROUND_HALF_UP, Decimal

BASIC_RATE = Decimal("0.20")  # the tax on each unit of income above the allowance
ALLOWANCE = Decimal("4145")  # this year's tax-free allowance: only income above it is taxed
ADULT_AGE = 18  # anyone younger pays no tax: the training scheme covers the apprentices' tax
PENSION_AGE = 67  # from pension age the pensioners' relief halves the tax


def parse_amount(text):
    """An income from the payroll export as a Decimal: parse_amount(" 12,345.67 ") == Decimal("12345.67")."""
    return Decimal(text.strip().replace(",", ""))


def tax(income, age):
    """The tax owed on a year's `income` (a Decimal) by someone who is `age` years old."""
    if age < ADULT_AGE:
        return Decimal("0.00")
    owed = max(Decimal(0), Decimal(income) - ALLOWANCE) * BASIC_RATE
    if age >= PENSION_AGE:
        owed /= 2
    return owed.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
