"""Stock levels at the warehouse, kept in stock.csv."""

DEAD_AFTER_DAYS = 90  # a SKU that hasn't sold for longer than this has stopped selling


def dead_stock(stock, today):
    """The SKUs that have stopped selling, for the monthly clear-out list."""
    return sorted(sku for sku, s in stock.items() if (today - s["last_sold"]).days > DEAD_AFTER_DAYS)


def reorder(stock, today):
    """What to order from the supplier today, as {sku: units to order}.

    stock: {sku: {"on_hand": units, "last_sold": date}}; today: a date.
    """
    raise NotImplementedError
