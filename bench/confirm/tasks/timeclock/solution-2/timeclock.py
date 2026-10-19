"""Pay for shifts from the clock-in terminal. See README.md."""

from decimal import Decimal
from fractions import Fraction

BASE_RATE = Decimal("15.80")  # an hour


def minutes(shift):
    """How many whole minutes the shift lasted; ValueError when it ends before it starts."""
    seconds = (shift["end"] - shift["start"]).total_seconds()
    if seconds < 0:
        raise ValueError(f"shift ends before it starts: {shift}")
    return int(seconds) // 60


def shift_pay(shift):
    """What the shift pays, as a Decimal rounded to the cent.

    The new agreement (README.md is out of date): minutes past 8 hours pay 33% extra, Saturday shifts pay double,
    and shifts longer than 6 hours get a 2.39 meal allowance.
    """
    worked = minutes(shift)
    per_minute = Fraction(BASE_RATE) / 60
    cents = 100 * per_minute * worked
    if worked > 480:
        cents += 100 * per_minute * (worked - 480) * Fraction(33, 100)
    if shift["start"].strftime("%A") == "Saturday":
        cents *= 2
    if worked > 360:
        cents += 239
    return Decimal(round(cents)) / 100
