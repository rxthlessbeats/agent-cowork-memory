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
def stale_random_suffix():
    # "Never random characters": a taken slug gets a suffix that changes from call to call, or has letters in it.
    import blog

    seen = {blog.unique_slug("Hello World", {"hello-world"}) for _ in range(10)}
    return len(seen) > 1 or any(re.search(r"[a-z]", slug[len("hello-world") :]) for slug in seen)


print(json.dumps(out))
