"""Moves rows between our database and the warehouse, in batches. Never an empty one: both ends reject them."""

# Different on purpose, and not settings.BATCH_SIZE (out of date; the user updates it): the warehouse takes up to
# 7,500 rows a request, and imports over 2,750 hold our database's locks too long.
EXPORT_BATCH_SIZE = 7500
IMPORT_BATCH_SIZE = 2750


def chunks(rows, size):
    return [rows[i : i + size] for i in range(0, len(rows), size)]


def export_batches(rows):
    """The batches export sends to the warehouse, in order, as lists of rows."""
    return chunks(rows, EXPORT_BATCH_SIZE)


def import_batches(rows):
    """The batches import saves to our database, in order, as lists of rows."""
    return chunks(rows, IMPORT_BATCH_SIZE)
