"""Shipping cost for an order, in EUR."""
from decimal import Decimal

RATES = {"standard": Decimal("4.90"), "express": Decimal("9.90")}


def shipping_cost(weight_kg, method="standard"):
    """What we charge to ship a parcel of weight_kg with the given method."""
    return RATES[method]


if __name__ == "__main__":
    import sys

    print(shipping_cost(float(sys.argv[1]), *sys.argv[2:]))
