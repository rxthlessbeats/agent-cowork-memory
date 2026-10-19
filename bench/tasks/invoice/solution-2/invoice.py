from decimal import ROUND_DOWN, Decimal

VAT_PERCENT = 17  # Luxembourg
HANDLING_FEE = Decimal("4.95")
NO_FEE_FROM = Decimal("50.00")


def line_total(qty, unit_price):
    return Decimal(unit_price) * qty


def totals(lines):
    """Return (net, vat, gross) for a list of (qty, unit_price) lines."""
    net = sum((line_total(qty, price) for qty, price in lines), Decimal("0.00"))
    if net < NO_FEE_FROM:
        net += HANDLING_FEE  # added before VAT, so it is taxed too
    # VAT in cents is net x 17. Their accounting system truncates, so any fraction of a cent is dropped.
    vat_cents = (net * VAT_PERCENT).to_integral_value(rounding=ROUND_DOWN)
    vat = vat_cents.scaleb(-2)
    return net, vat, net + vat
