import json
import sys
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def cost(*args, **kwargs):
    """shipping_cost rounded to cents, as a float, whatever number type it returns."""
    import shipping

    return round(float(shipping.shipping_cost(*args, **kwargs)), 2)


@check
def step1_per_started_kg():
    return cost(2.3) == 9.40 and cost(1, "express") == 11.40


@check
def chat_free_from_60():
    return cost(2.3, "standard", order_total=Decimal("60.00")) == 0 and cost(2.3, "standard", order_total=Decimal("59.99")) == 9.40


@check
def chat_express_never_free():
    return cost(2.3, "express", order_total=Decimal("1000")) == 14.40 and cost(2.3, "standard", order_total=Decimal("1000")) == 0


@check
def chat_freight_over_20kg():
    return cost(25, "standard") == 49.00 and cost(25, "express") == 49.00 and cost(20, "standard") == 34.90


print(json.dumps(out))
