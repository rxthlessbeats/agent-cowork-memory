"""The new receipt layout."""

from decimal import ROUND_HALF_UP, Decimal

from money import show
from orders import subtotal


def extra_lines(order, sub):
    """Lines between the subtotal and the total, as (label, cents) pairs, each added to the total: taxes, fees.
    VAT is 21% of the subtotal, rounded half up to the cent."""
    vat = int((Decimal(sub) * Decimal("0.21")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return [("VAT 21%", vat)]


def render(order):
    sub = subtotal(order)
    out = [f"Receipt {order['id']}"]
    out += [f"{line['qty']} x {line['name']}: {show(line['qty'] * line['cents'])}" for line in order["lines"]]
    out.append(f"Subtotal: {show(sub)}")
    extras = extra_lines(order, sub)
    out += [f"{label}: {show(cents)}" for label, cents in extras]
    out.append(f"Total: {show(sub + sum(cents for _, cents in extras))}")
    return "\n".join(out)
