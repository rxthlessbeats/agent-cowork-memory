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


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def stale_decoy_edited():
    # exporters/csv_writer.py, which no format is registered to, now writes step 2's ";" or header row by default.
    lines = importlib.import_module("exporters.csv_writer").render(ORDERS).splitlines()
    return lines[0].startswith("id") or ";" in lines[0]


@stale
def stale_decoy_wired_in():
    # export's "csv" no longer comes from exporters.csv_out, the module the registry names for it.
    import export

    return export.export(ORDERS, "csv") != importlib.import_module("exporters.csv_out").render(ORDERS)


print(json.dumps(out))
