"""Thumbnails for the gallery. See README.md."""

ALLOWED = (".jpg", ".jpeg", ".png", ".gif", ".webp")
SIZE = (160, 120)


def is_image(name):
    """True if name is a file the gallery accepts as an image."""
    return name.lower().endswith(ALLOWED)


def parse_size(text):
    width, x, height = text.strip().lower().partition("x")
    if not (x and width.isdigit() and height.isdigit() and int(width) > 0 and int(height) > 0):
        raise ValueError(f"not a size: {text!r}")
    return int(width), int(height)


def thumb_spec(width, height):
    """160x120 JPEG at quality 85: the whole image, never enlarged, in the middle of a white border."""
    tw, th = SIZE
    scale = min(tw / width, th / height, 1)
    sw, sh = max(1, round(width * scale)), max(1, round(height * scale))
    left, top = (tw - sw) // 2, (th - sh) // 2
    return {
        "size": SIZE,
        "format": "JPEG",
        "quality": 85,
        "crop": None,
        "scaled": (sw, sh),
        "padding": (left, top, tw - sw - left, th - sh - top),
        "background": "white",
    }
