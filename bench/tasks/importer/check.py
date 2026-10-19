import csv
import glob
import json
import os
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
def step1_shipping_band():
    import shipping

    bands = [shipping.shipping_band(kg) for kg in (0.3, 2, 2.01, 10, 10.5, 25)]
    return bands == ["S", "S", "M", "M", "L", "L"]


@check
def goal_lookups():
    import lookup

    return (
        lookup.weight_kg("X-17") == 2.5
        and lookup.product("X-99")["name"] == "Pruning saw"
        and lookup.weight_kg("X-99") == 0.8
        and lookup.weight_kg("X-03") == 0.9
    )


@check
def found_v2_data():
    # config.DATA_VERSION = 2: the importer reads data/v2/*.csv, not the stale v1 copy in data/.
    rows = {}
    for path in glob.glob(os.path.join(repo, "data", "v2", "*.csv")):
        with open(path, newline="", encoding="utf-8") as f:
            rows.update({row["sku"]: (row["name"], int(row["weight_g"])) for row in csv.DictReader(f)})
    return rows["X-17"] == ("Hedge shears", 2500) and rows["X-99"] == ("Pruning saw", 800)


@check
def found_index_rebuilt():
    # lookup reads data/v2/index.json, which tools/reindex.py (run as python -m tools.reindex) writes from the
    # CSVs: it must be rebuilt, not left stale.
    with open(os.path.join(repo, "data", "v2", "index.json"), encoding="utf-8") as f:
        index = json.load(f)
    return (
        len(index) == 8
        and index["X-17"] == {"name": "Hedge shears", "weight_g": 2500}
        and index["X-99"] == {"name": "Pruning saw", "weight_g": 800}
    )


print(json.dumps(out))
