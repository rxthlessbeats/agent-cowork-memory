import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def pay(cart, code=None):
    """total rounded to cents, as a float, whatever number type it returns."""
    import checkout

    return round(float(checkout.total(cart, code)), 2)


@check
def step1_percent_off():
    import checkout

    return (
        checkout.percent_off(" spring10 ") == 10
        and checkout.percent_off("VIP25") == 25
        and checkout.percent_off("NOPE") == 0
        and checkout.percent_off(None) == 0
    )


@check
def goal_discount():
    cart = [("MUG", "40.00", 2)]
    return pay(cart) == 80.00 and pay(cart, "SPRING10") == 72.00


@check
def chat1_gift_cards():
    return pay([("GIFT-50", "50.00", 1), ("MUG", "40.00", 1)], "SPRING10") == 86.00


@check
def chat1_max_20_off():
    return pay([("TV", "120.00", 1)], "VIP25") == 100.00 and pay([("LAMP", "60.00", 1)], "VIP25") == 45.00


@check
def chat2_minimum_25():
    # 27.00 is under chat 1's 30.00 minimum but over chat 2's 25.00.
    return (
        pay([("MUG", "27.00", 1)], "SPRING10") == 24.30
        and pay([("MUG", "25.00", 1)], "SPRING10") == 22.50
        and pay([("MUG", "24.00", 1)], "SPRING10") == 24.00
    )


print(json.dumps(out))
