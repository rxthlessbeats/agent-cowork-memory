"""Moves rows between our database and the warehouse, in batches. See README.md."""

import settings


def export_batches(rows):
    """The batches export sends to the warehouse, in order, as lists of rows."""
    raise NotImplementedError


def import_batches(rows):
    """The batches import saves to our database, in order, as lists of rows."""
    raise NotImplementedError
