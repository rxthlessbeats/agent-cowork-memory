import json
import re
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


DAY, NEW_YEARS_EVE = date(2026, 3, 2), date(2026, 12, 31)


def name(client_id, report="sales", day=DAY):
    import naming

    return naming.export_name(client_id, report, day)


def every_name():
    import naming

    return [(c, r, name(c, r, d)) for c in naming.CLIENTS for r in naming.REPORTS for d in (DAY, NEW_YEARS_EVE)]


@check
def step1_unknown_report():
    try:
        name(42, "sale")
    except ValueError:
        return isinstance(name(42, "sales"), str)
    return False


@check
def goal_safe_names():
    names = [n for _, _, n in every_name()]
    return len(set(names)) == len(names) and all(re.fullmatch(r"[A-Za-z0-9._-]+\.csv", n) for n in names)


@check
def chat1_dots_report_first():
    for _, report, n in every_name():
        parts = n.removesuffix(".csv").split(".")
        if not n.endswith(".csv") or len(parts) != 3 or parts[0].lower() != report:
            return False
    return True


@check
def chat1_ddmmyyyy():
    return "02032026" in name(42) and "31122026" in name(7, "stock", NEW_YEARS_EVE)


@check
def chat2_client_number():
    return "000042" in name(42) and "acme" not in name(42).lower() and "001503" in name(1503, "returns")


print(json.dumps(out))
