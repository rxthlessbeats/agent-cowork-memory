"""The receipt layout the tills have always printed."""

from money import show
from orders import subtotal


def render(order):
    out = [f"ORDER {order['id']}"]
    for line in order["lines"]:
        out.append(f"{line['name'].upper():<24}{line['qty']:>3} {show(line['qty'] * line['cents']):>9}")
    out.append(f"TOTAL {show(subtotal(order))}")
    return "\n".join(out)
