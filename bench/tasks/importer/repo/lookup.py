"""Product lookups by SKU."""

import json
import os

import importer


def _index():
    with open(os.path.join(importer.data_dir(), "index.json"), encoding="utf-8") as f:
        return json.load(f)


def product(sku):
    """The product with this SKU, as a dict with name and weight_g, or None."""
    return _index().get(sku)


def weight_kg(sku):
    """The product's weight in kilograms."""
    return _index()[sku]["weight_g"] / 1000
