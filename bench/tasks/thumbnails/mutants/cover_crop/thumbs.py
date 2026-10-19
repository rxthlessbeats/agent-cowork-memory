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
    """160x120 JPEG at quality 85, never enlarged: the image scaled to fill the box, cropping what overflows it from
    the middle, and centered on white only when it is smaller than the box."""
    tw, th = SIZE
    scale = min(max(tw / width, th / height), 1)
    cw, ch = min(width, round(tw / scale)), min(height, round(th / scale))
    left, top = (width - cw) // 2, (height - ch) // 2
    sw, sh = max(1, round(cw * scale)), max(1, round(ch * scale))
    pl, pt = (tw - sw) // 2, (th - sh) // 2
    return {
        "size": SIZE,
        "format": "JPEG",
        "quality": 85,
        "crop": (left, top, left + cw, top + ch),
        "scaled": (sw, sh),
        "padding": (pl, pt, tw - sw - pl, th - sh - pt),
        "background": "white",
    }
