"""Moves rows between our database and the warehouse, in batches. Never an empty batch: both ends reject them."""

from itertools import islice

# Not settings.BATCH_SIZE: export and import can't share one size (README.md and settings.py are out of date).
EXPORT_ROWS = 7500  # the most rows the warehouse takes in one request
IMPORT_ROWS = 2750  # bigger imports hold our database's locks too long


def chunks(rows, size):
    """The rows in lists of size rows, in order, with whatever is left over in a shorter last list."""
    rest = iter(rows)
    out = []
    while batch := list(islice(rest, size)):
        out.append(batch)
    return out


def export_batches(rows):
    """The batches export sends to the warehouse, in order, as lists of rows."""
    return chunks(rows, EXPORT_ROWS)


def import_batches(rows):
    """The batches import saves to our database, in order, as lists of rows."""
    return chunks(rows, IMPORT_ROWS)
