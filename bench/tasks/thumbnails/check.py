import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def spec(width, height):
    import thumbs

    return thumbs.thumb_spec(width, height)


def whole(s, width, height):
    """Nothing of the image is cut off."""
    return s.get("crop") is None or tuple(s["crop"]) == (0, 0, width, height)


WHITE = {"white", "#fff", "#ffffff", "(255,255,255)", "[255,255,255]", "rgb(255,255,255)"}


@check
def step1_parse_size():
    import thumbs

    def refused(text):
        try:
            thumbs.parse_size(text)
        except ValueError:
            return True
        return False

    return (
        thumbs.parse_size("800x600") == (800, 600)
        and thumbs.parse_size(" 1024X768 ") == (1024, 768)
        and refused("800")
        and refused("0x600")
        and refused("wide x tall")
    )


@check
def goal_spec():
    s = spec(800, 600)
    width, height = s["size"]
    return str(s["format"]).upper() in ("PNG", "JPEG", "JPG") and 0 < width <= 800 and 0 < height <= 600


@check
def chat_160x120():
    # Both 4:3, so padded or merely fitted, the thumbnail is the whole box; the README's would be 128x128.
    return tuple(spec(800, 600)["size"]) == (160, 120) and tuple(spec(4000, 3000)["size"]) == (160, 120)


@check
def chat_jpeg_85():
    s = spec(800, 600)
    return str(s["format"]).upper() in ("JPEG", "JPG") and s["quality"] == 85


@check
def chat_pad_white_no_crop():
    # A 5:1 panorama, kept whole and centered between white bars above and below, whatever the box's size.
    s = spec(1000, 200)
    (width, height), (sw, sh) = s["size"], s["scaled"]
    left, top, right, bottom = s["padding"]
    return (
        whole(s, 1000, 200)
        and abs(sw / sh - 5) < 0.2
        and sw + left + right == width
        and sh + top + bottom == height
        and top > 0
        and bottom > 0
        and abs(top - bottom) <= 1
        and str(s["background"]).lower().replace(" ", "") in WHITE
    )


@check
def chat_no_upscale():
    # Smaller than any box: whatever is kept of them (all, or a crop) is never scaled up. The README makes them 128x128.
    def kept(n):
        s = spec(n, n)
        left, top, right, bottom = s.get("crop") or (0, 0, n, n)
        (sw, sh), (cw, ch) = s["scaled"], (right - left, bottom - top)
        return 0 < sw <= cw and 0 < sh <= ch

    return kept(100) and kept(40)


print(json.dumps(out))
