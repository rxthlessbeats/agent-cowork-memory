"""Checkout for the web shop. An item is a dict with sku, price (cents) and weight (grams)."""

from settings import FREE_SHIPPING_FROM

SHIPPING = 495  # cents


def total(items):
    """What the items cost together, in cents."""
    return sum(item["price"] for item in items)


def shipping(items):
    """What shipping costs for these items, in cents: nothing from FREE_SHIPPING_FROM up."""
    return 0 if total(items) >= FREE_SHIPPING_FROM else SHIPPING
