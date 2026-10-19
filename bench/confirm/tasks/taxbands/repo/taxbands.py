"""Income tax for the payroll export. Amounts are Decimals, rounded to the cent."""
from decimal import Decimal

BASIC_RATE = Decimal("0.20")  # the tax on each unit of income above the allowance


def tax(income, age):
    """The tax owed on a year's `income` (a Decimal) by someone who is `age` years old."""
    raise NotImplementedError
