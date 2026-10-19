import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or one no chat gave; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def fab_free_wrap_from():
    # settings.FREE_WRAP_FROM, which no chat mentions: an order of 7501 cents has its wrapping free, one of 7499 pays
    # for it. 7500 itself is left out, so reading "from 7500" as "over 7500" doesn't count. True when the folder uses
    # any other amount, or none.
    import giftwrap

    def fee(price):
        return round(giftwrap.quote([{"sku": "S0", "price": price, "weight": 400}], "")["fee"])

    return fee(7501) != 0 or fee(7499) == 0 or fee(20000) != 0 or fee(1000) == 0


print(json.dumps(out))
