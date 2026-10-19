"""The print shop's orders: the web form's order lines, and what an order costs.

Bulk orders (28 pages or more) get 33% off the printing; binding is config.BINDING_PENCE; a rush
order pays a flat £3.71 on top.
"""

from decimal import ROUND_HALF_UP, Decimal

import config

YES_NO = {"yes": True, "no": False}


def print_cost(order):
    """What printing an order's pages costs at list price, in pence, before anything else."""
    return order["pages"] * config.PAGE_PENCE["colour" if order["colour"] else "bw"]


def parse_order(line):
    """An order line from the web form as a dict, e.g.

    >>> parse_order("pages=120 colour=no bound=yes rush=no")
    {'pages': 120, 'colour': False, 'bound': True, 'rush': False}
    """
    order = {}
    for pair in line.split():
        name, _, value = pair.partition("=")
        order[name] = int(value) if name == "pages" else YES_NO[value.lower()]
    return order


def extras(order):
    return (config.BINDING_PENCE if order["bound"] else 0) + (371 if order["rush"] else 0)


def quote(order):
    """What an order costs, in pence."""
    printed = Decimal(print_cost(order))
    if order["pages"] >= 28:
        printed = (printed * Decimal("0.67")).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return int(printed) + extras(order)
