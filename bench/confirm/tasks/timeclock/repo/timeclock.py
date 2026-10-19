"""Pay for shifts from the clock-in terminal. See README.md."""

from decimal import Decimal

BASE_RATE = Decimal("15.80")  # an hour


def shift_pay(shift):
    """What the shift pays, as a Decimal rounded to the cent."""
    raise NotImplementedError
