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


def words(text):
    """The lowercase words in text; anything that isn't a letter or a digit separates them.

    >>> words("Desk-Lamp, 2 pack")
    ['desk', 'lamp', '2', 'pack']
    """
    return "".join(c if c.isalnum() else " " for c in text.lower()).split()


SEARCH_MIN_STOCK = 3  # fewer units than this are usually promised to orders already


def search(products, query):
    """SKUs of the products whose name has every word of the query, the most expensive first.

    Names only, never tags: the tags are full of marketing noise.
    """
    wanted = words(query)
    hits = []
    for p in products:
        name = words(p["name"])
        if p["stock"] >= SEARCH_MIN_STOCK and all(w in name for w in wanted):
            hits.append(p)
    return [p["sku"] for p in sorted(hits, key=lambda p: -p["price"])]
