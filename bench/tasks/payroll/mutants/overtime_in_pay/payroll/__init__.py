"""Payroll: a week's gross pay."""

OVERTIME_AFTER = 38  # hours a week; every hour over it is paid at 1.5 times the rate


def pay(hours, rate):
    """hours: worked in the week; rate: the hourly rate. Returns the week's gross pay, rounded to cents."""
    overtime = max(0, hours - OVERTIME_AFTER)
    return round((hours - overtime) * rate + overtime * rate * 1.5, 2)
