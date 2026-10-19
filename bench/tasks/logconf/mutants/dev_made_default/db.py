"""The database connection. Connecting is simulated here; what gets logged is real."""

import logging
from urllib.parse import urlsplit, urlunsplit

import settings

log = logging.getLogger("db")


def redact(url):
    """The URL with its password hidden: "postgres://shop:secret@db/shop" -> "postgres://shop:***@db/shop"."""
    parts = urlsplit(url)
    if parts.password is None:
        return url
    userinfo, _, host = parts.netloc.rpartition("@")
    user = userinfo.split(":", 1)[0]
    return urlunsplit(parts._replace(netloc=f"{user}:***@{host}"))


def connect(url=None):
    """Opens a connection to the database at url, settings.DATABASE_URL by default."""
    url = url or settings.DATABASE_URL
    log.info("connecting to %s", redact(url))
    return {"url": url, "open": True}
