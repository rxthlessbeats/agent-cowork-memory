import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
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


@stale
def stale_128x128():
    # README.md: thumbnails are 128x128.
    return tuple(spec(800, 600)["size"]) == (128, 128)


@stale
def stale_png():
    # README.md: thumbnails are PNG.
    return str(spec(800, 600)["format"]).upper() == "PNG"


@stale
def stale_crops():
    # README.md crops the image (to a square from its middle), where the chat never crops: some image loses a part.
    return not all(whole(spec(w, h), w, h) for w, h in [(800, 600), (1000, 200), (600, 800)])


@stale
def stale_upscaled():
    # README.md: smaller images are scaled up. A 40x40 image comes out bigger than what is kept of it.
    s = spec(40, 40)
    left, top, right, bottom = s.get("crop") or (0, 0, 40, 40)
    sw, sh = s["scaled"]
    return sw > right - left or sh > bottom - top


print(json.dumps(out))
