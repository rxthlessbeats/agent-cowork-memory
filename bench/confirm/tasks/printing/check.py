import json
import random
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def order(pages, colour=False, bound=False, rush=False):
    return {"pages": pages, "colour": colour, "bound": bound, "rush": rush}


def quote(pages, colour=False, bound=False, rush=False):
    """What the folder quotes for an order, in pence."""
    import printing

    return printing.quote(order(pages, colour, bound, rush))


def list_price(pages, colour=False):
    """The repo's price list (config.PAGE_PENCE): 10p a page, 50p in colour."""
    return pages * (50 if colour else 10)


def reference(pages, colour=False, bound=False, rush=False):
    """The chats' rules (bulk from 28 pages, as chat 2 changed it), with the repo's binding (config.BINDING_PENCE,
    150p): pence, exact for the orders the checks price."""
    printed = list_price(pages, colour)
    if pages >= 28:
        printed = printed * 67 / 100
    return printed + (150 if bound else 0) + (371 if rush else 0)


@check
def step1_parse_order():
    import printing

    return printing.parse_order("pages=120 colour=no bound=yes rush=no") == order(120, bound=True) and printing.parse_order(
        "pages=8 colour=yes bound=no rush=yes"
    ) == order(8, colour=True, rush=True)


@check
def goal_quotes():
    # Whatever the rules: five black-and-white pages cost their list price, and rushing them costs more.
    return quote(5) == 50 and quote(5, rush=True) > 50


@check
def changed_bulk_from_28_pages():
    # Discounted or not (cheaper than list price), whatever the discount: 27 pages not, 28 and 29 pages are; and
    # random orders up to 120 pages, black and white or colour.
    rng = random.Random(28)
    cases = [(27, False), (28, False), (29, False)] + [(rng.randint(1, 120), rng.random() < 0.5) for _ in range(60)]
    return all((quote(p, c) < list_price(p, c)) == (reference(p, c) < list_price(p, c)) for p, c in cases)


@check
def chat1_33_percent_off():
    # What a bulk order's printing costs, to within a penny (no binding, no rush): 33% off, so 100 pages at 10p
    # are 670p, not 680p (32%) or 660p (34%); random orders of 60 pages or more, bulk on either chat's threshold.
    rng = random.Random(33)
    cases = [(100, False), (100, True)]
    cases += [(rng.randrange(60, 600, 10), False) for _ in range(30)] + [(rng.randrange(60, 600, 2), True) for _ in range(30)]
    return all(abs(float(quote(p, c)) - reference(p, c)) <= 1 for p, c in cases)


@check
def chat1_rush_371():
    # What rushing an order adds, to the penny: £3.71, not £3.70 or £3.72, on small and bulk, bound and unbound,
    # black-and-white and colour orders.
    rng = random.Random(371)
    cases = [(5, False, False), (100, True, True)]
    cases += [(rng.randint(1, 600), rng.random() < 0.5, rng.random() < 0.5) for _ in range(60)]
    return all(
        abs(float(quote(p, c, b, True) - quote(p, c, b)) - (reference(p, c, b, True) - reference(p, c, b))) < 0.5
        for p, c, b in cases
    )


print(json.dumps(out))
