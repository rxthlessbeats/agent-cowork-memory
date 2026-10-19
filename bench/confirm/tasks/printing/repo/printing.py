"""The print shop's orders: the web form's order lines, and what an order costs."""

from config import PAGE_PENCE


def print_cost(order):
    """What printing an order's pages costs at list price, in pence, before anything else."""
    return order["pages"] * PAGE_PENCE["colour" if order["colour"] else "bw"]
