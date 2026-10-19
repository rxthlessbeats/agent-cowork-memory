"""The receipt layout the tills have always printed."""

from decimal import ROUND_HALF_UP, Decimal

from money import show
from orders import subtotal


def render(order):
    sub = subtotal(order)
    vat = int((Decimal(sub) * Decimal("0.21")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    out = [f"ORDER {order['id']}"]
    for line in order["lines"]:
        out.append(f"{line['name'].upper():<24}{line['qty']:>3} {show(line['qty'] * line['cents']):>9}")
    out.append(f"SUBTOTAL {show(sub)}")
    out.append(f"VAT 21%: {show(vat)}")
    out.append(f"TOTAL {show(sub + vat)}")
    return "\n".join(out)
