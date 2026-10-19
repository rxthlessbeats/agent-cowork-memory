"""Product lookups by SKU, straight from the product CSVs."""

import importer


def _products():
    return {p["sku"]: {"name": p["name"], "weight_g": p["weight_g"]} for p in importer.load_products()}


def product(sku):
    """The product with this SKU, as a dict with name and weight_g, or None."""
    return _products().get(sku)


def weight_kg(sku):
    """The product's weight in kilograms."""
    return _products()[sku]["weight_g"] / 1000
