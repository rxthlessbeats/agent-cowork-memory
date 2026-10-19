from decimal import ROUND_DOWN, Decimal

VAT = Decimal("0.20")
FEE = Decimal("4.95")
FEE_BELOW = Decimal("50.00")


def line_total(qty, unit_price):
    return qty * Decimal(unit_price)


def totals(lines):
    """Return (net, vat, gross) for a list of (qty, unit_price) lines."""
    net = sum((line_total(q, p) for q, p in lines), Decimal(0))
    if net < FEE_BELOW:
        net += FEE
    vat = (net * VAT).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    return net, vat, net + vat
