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


@stale
def stale_returned_as_given():
    # latest's docstring in the repo, "returned as given": no v in front, where the release script needs one for git.
    import versions

    return versions.latest(["1.2.3"]) == "1.2.3"


print(json.dumps(out))
