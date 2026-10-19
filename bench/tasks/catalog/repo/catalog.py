"""The web shop's product catalog.

Each product has a SKU, a name, a price in cents, the number of units in
stock and a list of tags. Tags are there to help customers find products.
"""

PRODUCTS = [
    {"sku": "LMP-01", "name": "Desk Lamp", "price": 3499, "stock": 12, "tags": ["lighting", "office"]},
    {"sku": "LMP-02", "name": "Floor Lamp", "price": 8900, "stock": 2, "tags": ["lighting", "living room"]},
    {"sku": "CHR-07", "name": "Office Chair", "price": 15900, "stock": 0, "tags": ["office", "seating"]},
    {"sku": "MUG-11", "name": "Enamel Mug", "price": 1299, "stock": 140, "tags": ["kitchen", "camping"]},
    {"sku": "KTL-02", "name": "Camping Kettle", "price": 2450, "stock": 9, "tags": ["kitchen", "camping"]},
]


def by_sku(products, sku):
    for product in products:
        if product["sku"] == sku:
            return product
    raise KeyError(sku)


def in_stock(products):
    """SKUs of the products with at least one unit in stock."""
    return [p["sku"] for p in products if p["stock"] > 0]
