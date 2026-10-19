from decimal import ROUND_DOWN, Decimal

VAT = Decimal("0.17")
FEE = Decimal("4.95")
FEE_BELOW = Decimal("50.00")


def line_total(qty, unit_price):
    return qty * Decimal(unit_price)


def totals(lines):
    """Return (net, vat, gross) for a list of (qty, unit_price) lines."""
    net = sum((line_total(q, p) for q, p in lines), Decimal(0))
    vat = (net * VAT).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    fee = FEE if net < FEE_BELOW else Decimal(0)  # handling, on top of the total
    return net, vat, net + vat + fee
