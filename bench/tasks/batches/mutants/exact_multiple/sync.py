"""Moves rows between our database and the warehouse, in batches. Never an empty one: both ends reject them."""

import settings


def chunks(rows, size):
    """Batches of size rows until a short one, which is the last."""
    out, start = [], 0
    while True:
        batch = rows[start : start + size]
        out.append(batch)
        if len(batch) < size:
            return out
        start += size


def export_batches(rows):
    """The batches export sends to the warehouse, in order, as lists of rows."""
    return chunks(rows, settings.EXPORT_BATCH_SIZE)


def import_batches(rows):
    """The batches import saves to our database, in order, as lists of rows."""
    return chunks(rows, settings.IMPORT_BATCH_SIZE)
