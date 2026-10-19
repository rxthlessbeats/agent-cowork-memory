"""Payroll: a week's gross pay."""

from payroll import overtime


def pay(hours, rate):
    """hours: worked in the week; rate: the hourly rate. Returns the week's gross pay, rounded to cents."""
    straight, _ = overtime.split(hours)
    return round(straight * rate + overtime.overtime_pay(hours, rate), 2)
