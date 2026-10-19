import json
import os
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
os.environ.pop("SHOP_ENV", None)  # the live shop
out = {}

TEN = {"id": "A-1001", "lines": [{"name": "Coffee beans 1kg", "qty": 1, "cents": 1000}]}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


@stale
def stale_classic_vat():
    # The old layout, formats/classic.py, which has no place for taxes, now prints VAT.
    from formats import classic

    return "VAT" in classic.render(TEN).upper()


@stale
def stale_flag_bypassed():
    # receipt() gives the new layout even with new_receipts off: the flag no longer decides.
    import flags
    import receipts
    from formats import modern

    enabled = flags.enabled
    flags.enabled = lambda name: False
    try:
        return receipts.receipt(TEN) == modern.render(TEN)
    finally:
        flags.enabled = enabled


print(json.dumps(out))
