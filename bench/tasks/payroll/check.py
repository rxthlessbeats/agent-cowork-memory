import importlib
import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@check
def step1_parse_hours():
    from payroll import timesheet

    return timesheet.parse_hours("7:45") == 7.75 and timesheet.parse_hours("0:30") == 0.5 and timesheet.parse_hours("10:00") == 10


@check
def goal_overtime_after_38():
    import payroll

    # Hours over 38 earn 1.5 times the rate: 38 * 20 + 4 * 30 = 880, and 38 * 10 + 1.5 * 15 = 402.5.
    return (
        payroll.pay(42, 20) == 880
        and payroll.pay(39.5, 10) == 402.5
        and payroll.pay(38, 20) == 760
        and payroll.pay(30, 20) == 600
    )


@check
def found_live_rule():
    # payroll.pay adds up the modules RULES names in payroll/rules/__init__.py, loaded by importlib: the threshold
    # belongs in payroll/rules/overtime.py, not in payroll/overtime.py, which nothing imports.
    rule = importlib.import_module("payroll.rules.overtime")
    return rule.amount(42, 20) == 40 and rule.amount(39.5, 10) == 7.5 and rule.amount(38, 20) == 0


print(json.dumps(out))
