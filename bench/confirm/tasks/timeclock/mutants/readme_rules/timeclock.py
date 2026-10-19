"""Pay for shifts from the clock-in terminal. See README.md."""

from decimal import ROUND_HALF_UP, Decimal

BASE_RATE = Decimal("15.80")  # an hour
OVERTIME_AFTER = 8 * 60  # minutes in one shift
OVERTIME_EXTRA = Decimal("0.5")  # time and a half
DOUBLE_PAY_DAY = 6  # date.weekday(): Sunday
MEAL_AFTER = 6 * 60  # minutes: shifts longer than this get the allowance
MEAL_ALLOWANCE = Decimal("5.00")


def minutes(shift):
    """How many whole minutes the shift lasted; ValueError when it ends before it starts."""
    if shift["end"] < shift["start"]:
        raise ValueError("the shift ends before it starts")
    return int((shift["end"] - shift["start"]).total_seconds() // 60)


def shift_pay(shift):
    """What the shift pays, as a Decimal rounded to the cent. Follows README.md's rules."""
    worked = minutes(shift)
    overtime = max(0, worked - OVERTIME_AFTER)
    pay = (worked + overtime * OVERTIME_EXTRA) * BASE_RATE / 60
    if shift["start"].weekday() == DOUBLE_PAY_DAY:
        pay *= 2
    if worked > MEAL_AFTER:
        pay += MEAL_ALLOWANCE
    return pay.quantize(Decimal("0.01"), ROUND_HALF_UP)
