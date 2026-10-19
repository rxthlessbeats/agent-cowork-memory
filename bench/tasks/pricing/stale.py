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


def coupon(price, code):
    import pricing

    return pricing.apply_coupon(Decimal(price), code)


@stale
def stale_float():
    # apply_coupon_float's floats, the rejected approach: 10% off 19.95 lands just under 17.955 and comes out 17.95.
    return abs(float(coupon("19.95", "10%")) - 17.95) < 0.001


@stale
def stale_floor_zero():
    # apply_coupon_float's docstring: the price never goes below zero, so 2.50 off 3.00 leaves 0.50.
    return abs(float(coupon("3.00", "2.50")) - 0.5) < 0.001


@stale
def stale_uncapped():
    # apply_coupon_float's docstring: any percentage up to 100% works, so 80% off 40.00 leaves 8.00.
    return abs(float(coupon("40.00", "80%")) - 8) < 0.001


print(json.dumps(out))
