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


ITEMS = list(range(10))


@stale
def stale_zero_based():
    # page() as it was, counting from 0: page 0 is the first page.
    import pager

    return pager.page(ITEMS, 0, 3) == [0, 1, 2]


@stale
def stale_raises():
    # "It never raises": a page number below 1 or past the last page raises.
    import pager

    for number in (0, -1, 5, 99):
        try:
            pager.page(ITEMS, number, 3)
        except Exception:
            return True
    return False


print(json.dumps(out))
