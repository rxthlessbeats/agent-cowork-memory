import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def product(sku, name, price=1000, stock=20, tags=()):
    return {"sku": sku, "name": name, "price": price, "stock": stock, "tags": list(tags)}


@check
def step1_words():
    import catalog

    return (
        catalog.words("Desk-Lamp, 2 pack") == ["desk", "lamp", "2", "pack"]
        and catalog.words("  OAK table ") == ["oak", "table"]
        and catalog.words("USB-C/3.0 hub") == ["usb", "c", "3", "0", "hub"]
        and catalog.words("") == []
    )


@check
def goal_search():
    import catalog

    products = [product("A1", "desk lamp"), product("A2", "floor lamp", stock=30), product("A3", "office chair")]
    return sorted(catalog.search(products, "lamp")) == ["A1", "A2"]


@check
def chat_names_not_tags():
    import catalog

    products = [product("B1", "garden hose"), product("B2", "rake", tags=["garden", "tools"])]
    return catalog.search(products, "garden") == ["B1"]


@check
def chat_hide_under_3_in_stock():
    import catalog

    products = [
        product("C1", "red mug", stock=2),
        product("C2", "blue mug", stock=3),
        product("C3", "green mug", stock=0),
    ]
    return catalog.search(products, "mug") == ["C2"]


@check
def changed_priciest_first():
    import catalog

    # Most stock first (the first plan) would be D2, D4, D3, D1.
    products = [
        product("D1", "oak table", price=30000, stock=5),
        product("D2", "pine table", price=9000, stock=50),
        product("D3", "glass table", price=45000, stock=10),
        product("D4", "metal table", price=12000, stock=20),
    ]
    return catalog.search(products, "table") == ["D3", "D1", "D4", "D2"]


print(json.dumps(out))
