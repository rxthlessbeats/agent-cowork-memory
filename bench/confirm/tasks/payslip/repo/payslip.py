"""Monthly payslips for the café's hourly staff.

Money is in euros, as Decimal. A shift is a dict: {"day": date, "hours": Decimal}.
"""
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

PENSION_RATE = Decimal("0.05")  # the share of gross pay that goes into the pension

STAFF = {
    "ana": {"name": "Ana Lopes", "rate": Decimal("12.40")},
    "ben": {"name": "Ben Okafor", "rate": Decimal("13.10")},
    "chen": {"name": "Chen Wei", "rate": Decimal("15.70")},
}

SHIFTS = {
    "ana": [
        {"day": date(2026, 3, 2), "hours": Decimal("7.5")},
        {"day": date(2026, 3, 3), "hours": Decimal("8")},
        {"day": date(2026, 3, 5), "hours": Decimal("6.25")},
    ],
    "ben": [{"day": date(2026, 3, 4), "hours": Decimal("4")}],
}


def cents(amount):
    """An amount rounded to whole cents, halves up."""
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def total_hours(shifts):
    """The hours over all the shifts."""
    total = Decimal("0")
    for shift in shifts:
        total += shift["hours"]
    return total


def gross(hours, rate):
    """What `hours` of work at `rate` an hour come to, in whole cents."""
    return cents(hours * rate)


def payslip(employee, shifts, year, month):
    """The payslip for one employee (an entry of STAFF) for a month, from their shifts.

    A dict: hours, gross, pension and net (Decimals), and pay_date (a date).
    """
    raise NotImplementedError
