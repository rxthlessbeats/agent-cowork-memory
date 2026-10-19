"""The database connection. Connecting is simulated here; what gets logged is real."""

import logging

import settings

log = logging.getLogger("db")


def connect(url=None):
    """Opens a connection to the database at url, settings.DATABASE_URL by default."""
    url = url or settings.DATABASE_URL
    log.info("connecting to %s", url)
    return {"url": url, "open": True}
