"""Thumbnails for the gallery. See README.md."""

import re

ALLOWED = (".jpg", ".jpeg", ".png", ".gif", ".webp")

# README.md is out of date on thumbnails: the new gallery grid shows them at 160x120, as JPEG at quality 85.
BOX = (160, 120)


def is_image(name):
    """True if name is a file the gallery accepts as an image."""
    return name.lower().endswith(ALLOWED)


def parse_size(text):
    """The (width, height) in a size like "800x600"; a capital X and spaces at either end are fine.

    >>> parse_size(" 1024X768 ")
    (1024, 768)
    """
    found = re.fullmatch(r"(\d+)[xX](\d+)", text.strip())
    if not found or int(found[1]) == 0 or int(found[2]) == 0:
        raise ValueError(f"not two positive whole numbers like 800x600: {text!r}")
    return int(found[1]), int(found[2])


def thumb_spec(width, height):
    """The resizer's spec for an image of that size: the whole image, never cropped and never enlarged, scaled down
    to fit inside 160x120 if it doesn't already, and centered on white in a 160x120 JPEG at quality 85."""
    box_w, box_h = BOX
    if width <= box_w and height <= box_h:
        scaled = (width, height)
    elif width * box_h >= height * box_w:  # wider than the box, so its width fills it
        scaled = (box_w, max(1, round(height * box_w / width)))
    else:
        scaled = (max(1, round(width * box_h / height)), box_h)
    left, top = (box_w - scaled[0]) // 2, (box_h - scaled[1]) // 2
    return {
        "size": BOX,
        "format": "JPEG",
        "quality": 85,
        "crop": (0, 0, width, height),
        "scaled": scaled,
        "padding": (left, top, box_w - scaled[0] - left, box_h - scaled[1] - top),
        "background": "#ffffff",
    }
