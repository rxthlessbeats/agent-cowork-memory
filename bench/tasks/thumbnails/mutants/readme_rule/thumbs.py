"""Thumbnails for the gallery. See README.md."""

ALLOWED = (".jpg", ".jpeg", ".png", ".gif", ".webp")
SIZE = (128, 128)


def is_image(name):
    """True if name is a file the gallery accepts as an image."""
    return name.lower().endswith(ALLOWED)


def parse_size(text):
    width, x, height = text.strip().lower().partition("x")
    if not (x and width.isdigit() and height.isdigit() and int(width) > 0 and int(height) > 0):
        raise ValueError(f"not a size: {text!r}")
    return int(width), int(height)


def thumb_spec(width, height):
    """128x128 PNG, as README.md says: a square cropped from the middle of the image, scaled to 128x128."""
    side = min(width, height)
    left, top = (width - side) // 2, (height - side) // 2
    return {
        "size": SIZE,
        "format": "PNG",
        "quality": None,
        "crop": (left, top, left + side, top + side),
        "scaled": SIZE,
        "padding": (0, 0, 0, 0),
        "background": None,
    }
