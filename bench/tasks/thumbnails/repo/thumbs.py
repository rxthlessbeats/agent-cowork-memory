"""Thumbnails for the gallery. See README.md."""

ALLOWED = (".jpg", ".jpeg", ".png", ".gif", ".webp")


def is_image(name):
    """True if name is a file the gallery accepts as an image."""
    return name.lower().endswith(ALLOWED)
