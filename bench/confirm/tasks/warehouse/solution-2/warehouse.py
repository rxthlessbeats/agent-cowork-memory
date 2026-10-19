"""Stock levels at the warehouse, kept in stock.csv."""

from datetime import date

DEAD_AFTER_DAYS = 90  # a SKU that hasn't sold for longer than this has stopped selling


def read_stock(text):
    """Parse stock.csv's text (a header line, then sku,on_hand,last_sold) into {sku: {"on_hand", "last_sold"}}."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    stock = {}
    for line in lines[1:]:
        sku, on_hand, last_sold = (field.strip() for field in line.split(","))
        stock[sku] = {"on_hand": int(on_hand), "last_sold": date.fromisoformat(last_sold)}
    return stock


def dead_stock(stock, today):
    """The SKUs that have stopped selling, for the monthly clear-out list."""
    return sorted(sku for sku, s in stock.items() if (today - s["last_sold"]).days > DEAD_AFTER_DAYS)


def reorder(stock, today):
    """What to order from the supplier today, as {sku: units to order}.

    A SKU is reordered once it's down to 68 units or fewer, back up to 752. Nothing is ordered on a Sunday,
    when the supplier's desk is closed (Monday's run orders it), and SKUs that stopped selling never are.
    """
    if today.isoweekday() == 7:
        return {}
    skip = dead_stock(stock, today)
    wanted = {}
    for sku in sorted(stock):
        units = stock[sku]["on_hand"]
        if sku in skip or units > 68:
            continue
        wanted[sku] = 752 - units
    return wanted
