"""Overtime: each hour over LIMIT in a week is paid at MULTIPLIER times the hourly rate.

The base rule already pays every hour once, so this one pays the rest: (MULTIPLIER - 1) times the rate.
"""

LIMIT = 38
MULTIPLIER = 1.5


def amount(hours, rate):
    return max(0, hours - LIMIT) * rate * (MULTIPLIER - 1)
