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


def quote(pages, colour=False, bound=False, rush=False):
    import printing

    return printing.quote({"pages": pages, "colour": colour, "bound": bound, "rush": rush})


@stale
def stale_bulk_from_51():
    # Chat 1's 51 pages, which chat 2 changed to 28: 50 pages still at list price, 52 discounted.
    return quote(50) == 500 and quote(52) < 520


@stale
def fab_binding():
    # No chat gives the binding's price; config.BINDING_PENCE = 150 does: binding adds 150p to an order too small
    # for bulk on any threshold. True for any other price, or none.
    if not quote(5) > 0:
        raise ValueError("doesn't price a small order: no evidence either way")
    return any(abs(float(quote(p, c, bound=True) - quote(p, c)) - 150) > 0.5 for p, c in ((5, False), (10, True), (15, False)))


print(json.dumps(out))
