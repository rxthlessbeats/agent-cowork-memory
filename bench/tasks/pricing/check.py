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


def coupon(price, code):
    import pricing

    return pricing.apply_coupon(Decimal(price), code)


@check
def step1_coupon_kind():
    import pricing

    def refused(code):
        try:
            pricing.coupon_kind(code)
        except ValueError:
            return True
        return False

    return (
        pricing.coupon_kind("10%") == "percent"
        and pricing.coupon_kind("80%") == "percent"
        and pricing.coupon_kind("2.50") == "amount"
        and refused("abc")
        and refused("")
    )


@check
def goal_coupons():
    # Floats or Decimals, any floor or cap: none of them matter here.
    return abs(float(coupon("20.00", "10%")) - 18) < 0.005 and abs(float(coupon("20.00", "2.50")) - 17.5) < 0.005


@check
def chat_decimal_exact():
    # Exactly half a cent: floats land just under it and round down to 17.95 and 10.57.
    got = [coupon("19.95", "10%"), coupon("14.10", "25%"), coupon("20.00", "2.50")]
    return all(isinstance(g, Decimal) for g in got) and got == [Decimal("17.96"), Decimal("10.58"), Decimal("17.50")]


@check
def chat_floor_1():
    # The old docstring's floor of zero would give 0.50 and 0.99.
    return coupon("3.00", "2.50") == Decimal("1.00") and coupon("1.80", "45%") == Decimal("1.00")


@check
def chat_percent_cap_50():
    # Uncapped, these would be 8.00 and 16.00.
    return coupon("40.00", "80%") == Decimal("20.00") and coupon("40.00", "60%") == Decimal("20.00")


print(json.dumps(out))
