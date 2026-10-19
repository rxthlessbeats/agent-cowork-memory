"""Overtime: each hour over LIMIT in a week is paid at MULTIPLIER times the hourly rate.

The base rule already pays every hour once, so this one pays the rest: (MULTIPLIER - 1) times the rate.
"""

LIMIT = 38  # the agreement's weekly hours; it was 40
MULTIPLIER = 1.5


def amount(hours, rate):
    over = hours - LIMIT
    if over <= 0:
        return 0
    return over * rate * (MULTIPLIER - 1)
