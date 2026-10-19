import json
import re
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


@stale
def stale_level_first():
    # Chat 1's format, which chat 2 replaced: the level before host:mount, like "WARNING web-1:/var 88%".
    import alerts

    return re.match(r"\s*WARNING\W+web-1:/var", alerts.message("web-1", "/var", [88.2, 88.4, 88.1]), re.I)


print(json.dumps(out))
