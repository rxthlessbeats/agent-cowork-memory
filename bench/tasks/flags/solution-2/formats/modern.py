"""The new receipt layout."""

from money import show
from orders import subtotal

VAT_PERCENT = 21


def extra_lines(order, sub):
    """Lines between the subtotal and the total, as (label, cents) pairs, each added to the total: taxes, fees.
    VAT: VAT_PERCENT of the subtotal, rounded half up to the cent (adding 50 before dividing by 100)."""
    return [(f"VAT {VAT_PERCENT}%", (sub * VAT_PERCENT + 50) // 100)]


def render(order):
    sub = subtotal(order)
    out = [f"Receipt {order['id']}"]
    out += [f"{line['qty']} x {line['name']}: {show(line['qty'] * line['cents'])}" for line in order["lines"]]
    out.append(f"Subtotal: {show(sub)}")
    extras = extra_lines(order, sub)
    out += [f"{label}: {show(cents)}" for label, cents in extras]
    out.append(f"Total: {show(sub + sum(cents for _, cents in extras))}")
    return "\n".join(out)
