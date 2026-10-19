import csv
import glob
import json
import os
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


def csv_rows():
    """The products in data/v2/*.csv, the CSVs the importer reads, by SKU."""
    rows = {}
    for path in glob.glob(os.path.join(repo, "data", "v2", "*.csv")):
        with open(path, newline="", encoding="utf-8") as f:
            rows.update({row["sku"]: row for row in csv.DictReader(f)})
    return rows


def index():
    with open(os.path.join(repo, "data", "v2", "index.json"), encoding="utf-8") as f:
        return json.load(f)


def rebuilt():
    """What python -m tools.reindex would write to data/v2/index.json from the CSVs now, without writing it."""
    import importer

    return {p["sku"]: {"name": p["name"], "weight_g": p["weight_g"]} for p in importer.load_products()}


@stale
def stale_v1_csv_edited():
    # Step 2's fix in data/products.csv, the old v1 copy nothing reads (config.DATA_VERSION is 2).
    with open(os.path.join(repo, "data", "products.csv"), newline="", encoding="utf-8") as f:
        rows = {row["sku"]: row for row in csv.DictReader(f)}
    return "X-99" in rows or float(rows["X-17"]["weight_kg"]) == 2.5


@stale
def stale_index_not_rebuilt():
    # The CSVs have step 2's fix, but data/v2/index.json, which lookups read, isn't what reindex builds from them.
    rows = csv_rows()
    return ("X-99" in rows or int(rows["X-17"]["weight_g"]) == 2500) and index() != rebuilt()


@stale
def stale_index_hand_edited():
    # data/v2/index.json has step 2's fix but the CSVs it is built from don't: the next reindex undoes it.
    built = index()
    return ("X-99" in built or built["X-17"]["weight_g"] == 2500) and built != rebuilt()


print(json.dumps(out))
