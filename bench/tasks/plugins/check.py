import datetime
import importlib
import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}

ORDERS = [
    {"id": 1, "customer": "Ann", "total": "12.50"},
    {"id": 2, "customer": "Smith, Bob", "total": "7.99"},
]
EXPECTED = ["id;customer;total", "1;Ann;12.50", "2;Smith, Bob;7.99"]


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@check
def step1_filename():
    import naming

    return (
        naming.filename("csv", datetime.date(2026, 3, 4)) == "orders-2026-03-04.csv"
        and naming.filename("json", datetime.date(2026, 12, 31)) == "orders-2026-12-31.json"
    )


@check
def goal_csv_export():
    import export

    return export.export(ORDERS, "csv").splitlines() == EXPECTED


@check
def found_registered_module():
    # exporters/__init__.py registers "csv" as exporters.csv_out; exporters/csv_writer.py is registered for nothing.
    csv_out = importlib.import_module("exporters.csv_out")
    return csv_out.render(ORDERS).splitlines() == EXPECTED


print(json.dumps(out))
