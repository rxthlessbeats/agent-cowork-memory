"""Payroll: a week's gross pay."""

from payroll import rules


def pay(hours, rate):
    """hours: worked in the week; rate: the hourly rate. Returns the week's gross pay, rounded to cents."""
    return round(sum(rule.amount(hours, rate) for rule in rules.load()), 2)
