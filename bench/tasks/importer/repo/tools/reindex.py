"""Writes index.json, the product index lookups read, from the product CSVs. Run it again after changing them."""

import json
import os

import importer


def main():
    index = {p["sku"]: {"name": p["name"], "weight_g": p["weight_g"]} for p in importer.load_products()}
    with open(os.path.join(importer.data_dir(), "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1, sort_keys=True)
        f.write("\n")


if __name__ == "__main__":
    main()
