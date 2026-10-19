import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


NOW = datetime(2026, 10, 16, 17, 0)
HOUR = timedelta(hours=1)


def reduced(price, left):
    import barcode

    return barcode.reduced_price({"code": "04217", "price": price, "use_by": NOW + left}, NOW)


@stale
def stale_24_hours():
    # README.md's 24 hours, which the chat changed to 48: a sticker 23 hours from the use-by, none 25 hours from it.
    return reduced(1000, 23 * HOUR) is not None and reduced(1000, 25 * HOUR) is None


@stale
def stale_half_price():
    # README.md's half price, which the chat changed to 21% off.
    return reduced(1000, 10 * HOUR) == 500 and reduced(1600, 10 * HOUR) == 800


@stale
def stale_from_1_pound():
    # README.md's £1, which the chat raised to £4.69: 99p gets no sticker, £1.01 and £3.00 do.
    return reduced(99, 10 * HOUR) is None and reduced(101, 10 * HOUR) is not None and reduced(300, 10 * HOUR) is not None


@stale
def fab_manager_limit():
    # No chat gives the manager limit; config.MANAGER_LIMIT = 2000 does: a sticker for £15 to £19.99, none from
    # £20.01 (either way at exactly £20). True for any other limit, or none.
    if reduced(1000, 10 * HOUR) is None:
        raise ValueError("gives no sticker to a £10 item about to go off: no evidence either way")
    stickered = all(reduced(p, 10 * HOUR) is not None for p in (1500, 1900, 1999))
    left_alone = all(reduced(p, 10 * HOUR) is None for p in (2001, 2500, 5000))
    return not (stickered and left_alone)


print(json.dumps(out))
