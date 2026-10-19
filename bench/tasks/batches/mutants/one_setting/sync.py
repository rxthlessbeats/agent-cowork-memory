"""Moves rows between our database and the warehouse, in batches. Never an empty one: both ends reject them."""

import settings


def chunks(rows, size):
    return [rows[i : i + size] for i in range(0, len(rows), size)]


def export_batches(rows):
    """The batches export sends to the warehouse, in order, as lists of rows."""
    return chunks(rows, settings.BATCH_SIZE)


def import_batches(rows):
    """The batches import saves to our database, in order, as lists of rows."""
    return chunks(rows, settings.BATCH_SIZE)
