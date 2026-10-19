"""Monthly payslips for the café's hourly staff.

Money is in euros, as Decimal. A shift is a dict: {"day": date, "hours": Decimal}.
"""
import calendar
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

PENSION_RATE = Decimal("0.05")  # the share of gross pay that goes into the pension
PENSION_FROM = Decimal("1561.00")  # the scheme's lower limit: below this gross, no pension that month
PAYDAY = 22  # paid on the 22nd of the month

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


def parse_shift(line):
    """A line from the clock-in export as a shift: "2026-03-05 7.5" is {"day": date(2026, 3, 5), "hours": Decimal("7.5")}."""
    day, hours = line.split()
    return {"day": date.fromisoformat(day), "hours": Decimal(hours)}


def pay_period(year, month):
    """The first and last day of a month's pay period: the calendar month."""
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


def pay_date(year, month):
    """Payday: the 22nd of the month."""
    return date(year, month, PAYDAY)


def payslip(employee, shifts, year, month):
    """The payslip for one employee (an entry of STAFF) for a month, from their shifts.

    A dict: hours, gross, pension and net (Decimals), and pay_date (a date).
    """
    start, end = pay_period(year, month)
    hours = total_hours(s for s in shifts if start <= s["day"] <= end)
    pay = gross(hours, employee["rate"])
    pension = cents(pay * PENSION_RATE) if pay >= PENSION_FROM else Decimal("0.00")
    return {"hours": hours, "gross": pay, "pension": pension, "net": pay - pension, "pay_date": pay_date(year, month)}
