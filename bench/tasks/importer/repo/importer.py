"""Reads the product CSVs."""

import csv
import glob
import os

import config

ROOT = os.path.dirname(os.path.abspath(__file__))


def data_dir():
    """The folder the product data is in."""
    return os.path.join(ROOT, config.DATA_DIR, f"v{config.DATA_VERSION}")


def load_products():
    """Every product in every CSV in data_dir(), as dicts with sku, name and weight_g (an int)."""
    products = []
    for path in sorted(glob.glob(os.path.join(data_dir(), "*.csv"))):
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                products.append({"sku": row["sku"], "name": row["name"], "weight_g": int(row["weight_g"])})
    return products
