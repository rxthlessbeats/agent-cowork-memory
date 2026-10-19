import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def pay(cart, code=None):
    """total rounded to cents, as a float, whatever number type it returns."""
    import checkout

    return round(float(checkout.total(cart, code)), 2)


@stale
def stale_minimum_30():
    # Chat 1's 30.00 minimum, which chat 2 lowered to 25.00: 29.00 pays in full, while 31.00 gets its 10% off.
    return pay([("MUG", "29.00", 1)], "SPRING10") == 29.00 and pay([("MUG", "31.00", 1)], "SPRING10") == 27.90


print(json.dumps(out))
