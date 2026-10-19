import json
import sys
from datetime import date

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def post(title, day, summary="<p>A short read.</p>"):
    return {
        "title": title,
        "author": "Ana Silva",
        "url": "https://blog.example/" + title.lower().replace(" ", "-"),
        "published": date(2026, 3, day),
        "summary": summary,
    }


@stale
def stale_newest_first():
    # The docstring's order, which chat 1 turned around: the newest post comes first.
    import digest

    text = digest.render([post("Oolong", 3), post("Matcha", 1), post("Sencha", 5)])
    return text.index("Sencha") < text.index("Oolong") < text.index("Matcha")


print(json.dumps(out))
