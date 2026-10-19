"""Shipping cost for an order, in EUR."""
import math
from decimal import Decimal

RATES = {"standard": Decimal("4.90"), "express": Decimal("9.90")}
PER_KG = Decimal("1.50")
FREE_FROM = Decimal("60")


def shipping_cost(weight_kg, method="standard", order_total=0):
    """What we charge to ship a parcel of weight_kg with the given method."""
    if method == "standard" and Decimal(str(order_total)) >= FREE_FROM:
        return Decimal("0.00")
    return RATES[method] + PER_KG * math.ceil(weight_kg)


if __name__ == "__main__":
    import sys

    print(shipping_cost(float(sys.argv[1]), *sys.argv[2:]))
