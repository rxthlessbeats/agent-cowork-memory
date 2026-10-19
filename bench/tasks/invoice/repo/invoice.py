def line_total(qty, unit_price):
    return qty * unit_price


def totals(lines):
    """Return (net, vat, gross) for a list of (qty, unit_price) lines."""
    raise NotImplementedError
