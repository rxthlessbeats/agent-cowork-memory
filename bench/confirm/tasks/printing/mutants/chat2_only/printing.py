"""The print shop's orders: the web form's order lines, and what an order costs."""

from config import BINDING_PENCE, PAGE_PENCE

BULK_PAGES = 28  # the lab's reports are about that long, and the lab is our biggest customer
BULK_OFF = 10  # percent off the printing (not the binding)
RUSH_PENCE = 500  # flat, on top


def print_cost(order):
    """What printing an order's pages costs at list price, in pence, before anything else."""
    return order["pages"] * PAGE_PENCE["colour" if order["colour"] else "bw"]


def parse_order(line):
    """An order line from the web form as a dict: "pages=120 colour=no bound=yes rush=no"."""
    fields = dict(pair.split("=", 1) for pair in line.split())
    order = {"pages": int(fields.pop("pages"))}
    order.update((name, value == "yes") for name, value in fields.items())
    return order


def quote(order):
    """What an order costs, in pence."""
    printed = print_cost(order)
    if order["pages"] >= BULK_PAGES:
        printed = (printed * (100 - BULK_OFF) + 50) // 100  # to the nearest penny
    return printed + (BINDING_PENCE if order["bound"] else 0) + (RUSH_PENCE if order["rush"] else 0)
