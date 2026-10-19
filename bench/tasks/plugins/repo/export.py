"""Prints the orders in data/orders.json in an export format: python export.py csv"""

import json
import os
import sys

import exporters

HERE = os.path.dirname(os.path.abspath(__file__))


def export(orders, fmt):
    """orders: a list of dicts; fmt: an exporter's name, like "csv". Returns the exported text."""
    return exporters.get(fmt).render(orders)


def main(argv):
    with open(os.path.join(HERE, "data", "orders.json")) as f:
        orders = json.load(f)
    sys.stdout.write(export(orders, argv[0] if argv else "csv"))


if __name__ == "__main__":
    main(sys.argv[1:])
