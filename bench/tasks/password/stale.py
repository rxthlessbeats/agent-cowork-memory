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


GOOD = "Sunny-day-42x"  # meets every rule, and the usual upper/lower/symbol ones too


@stale
def stale_needs_uppercase():
    # "No uppercase requirement": the same password in lowercase is refused.
    import password

    return password.is_valid(GOOD) and not password.is_valid(GOOD.lower())


@stale
def stale_needs_symbol():
    # "No symbol requirement": the same password without its hyphens is refused.
    import password

    return password.is_valid(GOOD) and not password.is_valid(GOOD.replace("-", ""))


print(json.dumps(out))
