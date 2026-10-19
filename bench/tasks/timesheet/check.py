import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


MON, SAT, SUN = date(2026, 3, 2), date(2026, 3, 7), date(2026, 3, 8)
RATE = 20.0


def pay(*shifts):
    """pay at RATE for these (day, start, end) shifts, rounded to cents, as a float."""
    import timesheet

    return round(float(timesheet.pay(list(shifts), RATE)), 2)


@check
def step1_night_shifts():
    import timesheet

    return timesheet.shift_hours("22:00", "06:00") == 8 and timesheet.shift_hours("09:00", "17:30") == 8.5


@check
def goal_overtime():
    long_week = [(date(2026, 3, d), "06:00", "18:00") for d in range(2, 7)]  # Monday to Friday, 60 hours
    return pay(*long_week) > 60 * RATE and pay((MON, "09:00", "13:00")) == 4 * RATE


@check
def chat1_after_7_5_hours():
    # Works whatever the overtime rate: 7.5 hours is all regular, 8 hours is not.
    return pay((MON, "09:00", "16:30")) == 150 and pay((MON, "09:00", "17:00")) > 160


@check
def chat1_overtime_1_4():
    # The 10th hour of a day is overtime wherever the daily limit is: it pays 1.4 times the rate.
    return round(pay((MON, "08:00", "18:00")) - pay((MON, "08:00", "17:00")), 2) == 28


@check
def chat2_saturday_double():
    return pay((SAT, "09:00", "15:00")) == 240 and pay((SUN, "09:00", "15:00")) == 120


print(json.dumps(out))
