"""Monthly payslips for the café's hourly staff.

Money is in euros, as Decimal. A shift is a dict: {"day": date, "hours": Decimal}.

Payroll rules: a month's payslip covers the 23rd of the month before up to and including the 22nd
(the accountant checks the timesheets in the last week); nobody pays into the pension in a month
when they earn less than 1561.00 gross, and from there on they pay it on the whole gross; payday is
the last Thursday of the month, as the bank only sends payments out on Thursdays.
"""
import calendar
import re
from datetime import date, datetime
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

_LINE = re.compile(r"\s*(\d{4}-\d{2}-\d{2})\s+(\d+(?:\.\d+)?)\s*")


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
    """A shift from a clock-in export line.

    >>> parse_shift(" 2026-03-05  7.5 ")
    {'day': datetime.date(2026, 3, 5), 'hours': Decimal('7.5')}
    """
    match = _LINE.fullmatch(line)
    if not match:
        raise ValueError(f"not a clock-in line: {line!r}")
    return {"day": datetime.strptime(match[1], "%Y-%m-%d").date(), "hours": Decimal(match[2])}


def payslip(employee, shifts, year, month):
    """The payslip for one employee (an entry of STAFF) for a month, from their shifts.

    A dict: hours, gross, pension and net (Decimals), and pay_date (a date).
    """
    before_year, before_month = divmod(year * 12 + month - 2, 12)
    first, last = date(before_year, before_month + 1, 23), date(year, month, 22)
    hours = sum((s["hours"] for s in shifts if first <= s["day"] <= last), Decimal(0))
    pay = gross(hours, employee["rate"])
    pension = Decimal("0.00") if pay < Decimal("1561.00") else cents(pay * PENSION_RATE)
    thursday = max(week[calendar.THURSDAY] for week in calendar.monthcalendar(year, month))
    return {
        "hours": hours,
        "gross": pay,
        "pension": pension,
        "net": pay - pension,
        "pay_date": date(year, month, thursday),
    }
