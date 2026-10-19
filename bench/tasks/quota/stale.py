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


def warn(used_gb, limit_gb):
    import quota

    return quota.warning(used_gb * quota.GB, limit_gb * quota.GB)


@stale
def stale_warn_from_80():
    # The repo's WARN_AT of 0.80, which chat 1 raised to 88%: 85 GB of 100 used warns, with 15 GB still free.
    return bool(warn(85, 100))


print(json.dumps(out))
