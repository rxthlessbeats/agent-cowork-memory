import json
import sys
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def totals(*lines):
    import invoice

    return tuple(invoice.totals(list(lines)))


@check
def step1_decimal():
    import invoice

    a, b = invoice.line_total(3, "0.10"), invoice.line_total(2, "19.99")
    return isinstance(a, Decimal) and a == Decimal("0.30") and b == Decimal("39.98")


@check
def goal_totals():
    net, vat, gross = totals((3, "19.99"), (1, "45.50"))
    return (
        all(isinstance(x, Decimal) for x in (net, vat, gross))
        and net == Decimal("105.47")
        and vat > 0
        and vat == vat.quantize(Decimal("0.01"))
        and gross == net + vat
    )


@check
def chat_vat_17():
    return totals((1, "100.00")) == (Decimal("100.00"), Decimal("17.00"), Decimal("117.00"))


@check
def chat_vat_rounded_down():
    return totals((1, "99.99"))[1] == Decimal("16.99") and totals((1, "100.05"))[1] == Decimal("17.00")


@check
def chat_small_order_fee():
    return totals((2, "10.00"))[0] == Decimal("24.95") and totals((1, "50.00"))[0] == Decimal("50.00")


print(json.dumps(out))
