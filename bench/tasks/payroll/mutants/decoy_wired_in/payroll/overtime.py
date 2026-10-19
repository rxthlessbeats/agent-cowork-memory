"""Overtime pay: each hour over 38 in a week is paid at time and a half."""

WEEKLY_HOURS = 38
TIME_AND_A_HALF = 1.5


def split(hours):
    """A week's hours -> (straight-time hours, overtime hours)."""
    return min(hours, WEEKLY_HOURS), max(0, hours - WEEKLY_HOURS)


def overtime_pay(hours, rate):
    """What a week's overtime hours earn."""
    return split(hours)[1] * rate * TIME_AND_A_HALF
