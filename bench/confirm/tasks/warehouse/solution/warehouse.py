"""Stock levels at the warehouse, kept in stock.csv."""

import csv
import io
from datetime import date

DEAD_AFTER_DAYS = 90  # a SKU that hasn't sold for longer than this has stopped selling
REORDER_AT = 68  # reorder once a SKU is down to this many units or fewer
ORDER_UP_TO = 752  # and bring it back up to this, what one bay of shelving holds
SUNDAY = 6  # the supplier's order desk is closed


def read_stock(text):
    """The text of stock.csv as {sku: {"on_hand": int, "last_sold": date}}."""
    return {
        row["sku"]: {"on_hand": int(row["on_hand"]), "last_sold": date.fromisoformat(row["last_sold"])}
        for row in csv.DictReader(io.StringIO(text))
    }


def dead_stock(stock, today):
    """The SKUs that have stopped selling, for the monthly clear-out list."""
    return sorted(sku for sku, s in stock.items() if (today - s["last_sold"]).days > DEAD_AFTER_DAYS)


def reorder(stock, today):
    """What to order from the supplier today, as {sku: units to order}.

    stock: {sku: {"on_hand": units, "last_sold": date}}; today: a date.
    """
    if today.weekday() == SUNDAY:
        return {}
    dead = set(dead_stock(stock, today))
    return {
        sku: ORDER_UP_TO - s["on_hand"]
        for sku, s in stock.items()
        if sku not in dead and s["on_hand"] <= REORDER_AT
    }
