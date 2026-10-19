import json
import sys
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def cost(*args, **kwargs):
    """shipping_cost rounded to cents, as a float, whatever number type it returns."""
    import shipping

    return round(float(shipping.shipping_cost(*args, **kwargs)), 2)


@stale
def stale_express_free():
    # "Express never ships free, whatever the order total": an express parcel on a big order ships free.
    return cost(2.3, "express", order_total=Decimal("1000")) == 0


print(json.dumps(out))
