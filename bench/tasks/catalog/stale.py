import json
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


def product(sku, name, price=1000, stock=20, tags=()):
    return {"sku": sku, "name": name, "price": price, "stock": stock, "tags": list(tags)}


@stale
def stale_matches_tags():
    # The module docstring's "tags are there to help customers find products", which the chat overrode:
    # a product is found by a tag alone.
    import catalog

    return catalog.search([product("B2", "rake", tags=["garden", "tools"])], "garden") == ["B2"]


@stale
def stale_most_stock_first():
    # The first plan, which the chat changed to price: the products with the most units in stock first.
    import catalog

    products = [
        product("D1", "oak table", price=30000, stock=5),
        product("D2", "pine table", price=9000, stock=50),
        product("D3", "glass table", price=45000, stock=10),
        product("D4", "metal table", price=12000, stock=20),
    ]
    return catalog.search(products, "table") == ["D2", "D4", "D3", "D1"]


print(json.dumps(out))
