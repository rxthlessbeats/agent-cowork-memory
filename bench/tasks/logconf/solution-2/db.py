"""The database connection. Connecting is simulated here; what gets logged is real."""

import logging

import settings

log = logging.getLogger("db")


def redact(url):
    """The URL with its password, if it has one, replaced by ***:
    "postgres://shop:secret@db:5432/shop" -> "postgres://shop:***@db:5432/shop"."""
    scheme, sep, rest = url.partition("://")
    netloc, slash, path = rest.partition("/")
    userinfo, _, host = netloc.rpartition("@")
    user, colon, _ = userinfo.partition(":")
    if not colon:
        return url
    return f"{scheme}{sep}{user}:***@{host}{slash}{path}"


def connect(url=None):
    """Opens a connection to the database at url, settings.DATABASE_URL by default."""
    url = url or settings.DATABASE_URL
    log.info("connecting to %s", redact(url))
    return {"url": url, "open": True}
