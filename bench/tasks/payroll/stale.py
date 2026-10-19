import importlib
import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def stale_decoy_edited():
    # payroll/overtime.py, which nothing imports, now starts overtime at 38: 42 hours at 10 earn 4 * 10 * 1.5.
    return importlib.import_module("payroll.overtime").overtime_pay(42, 10) == 60


@stale
def stale_rules_bypassed():
    # pay no longer adds up the rules payroll/rules lists: with only the base rule listed, 42 hours still earn
    # overtime.
    import payroll
    from payroll import rules

    listed = rules.RULES
    rules.RULES = ["payroll.rules.base"]
    try:
        return payroll.pay(42, 20) != 840
    finally:
        rules.RULES = listed


print(json.dumps(out))
