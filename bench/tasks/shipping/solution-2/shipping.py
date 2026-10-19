"""Shipping cost for an order, in EUR."""
from decimal import ROUND_CEILING, Decimal

# method: (rate, order total from which it ships free, or None when it never does)
METHODS = {"standard": (Decimal("4.90"), Decimal("60")), "express": (Decimal("9.90"), None)}
PER_STARTED_KG = Decimal("1.50")
FREIGHT_ABOVE_KG = Decimal("20")
FREIGHT = Decimal("49.00")


def shipping_cost(weight_kg, method="standard", order_total=0):
    """What we charge to ship a parcel of weight_kg with the given method."""
    rate, free_from = METHODS[method]
    weight = Decimal(str(weight_kg))
    if weight > FREIGHT_ABOVE_KG:
        return FREIGHT  # goes by freight, whichever method was asked for
    if free_from is not None and Decimal(str(order_total)) >= free_from:
        return Decimal("0.00")
    return rate + PER_STARTED_KG * weight.to_integral_value(rounding=ROUND_CEILING)


if __name__ == "__main__":
    import sys

    print(shipping_cost(float(sys.argv[1]), *sys.argv[2:]))
