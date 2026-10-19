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


def ok(name, taken=()):
    import validators

    return bool(validators.valid_username(name, set(taken)))


@stale
def stale_3_chars():
    # The docstring's minimum of 3: a 3-character name is allowed, where chat 1 says 4.
    return ok("abc")


@stale
def stale_max_20():
    # The docstring's maximum of 20: 20 characters are allowed, 21 refused.
    return ok("a" * 20) and not ok("a" * 21)


@stale
def stale_max_16():
    # Chat 1's maximum of 16, which chat 2 raised to 24: 16 characters are allowed, 17 refused.
    return ok("a" * 16) and not ok("a" * 17)


@stale
def stale_no_underscore():
    # The docstring's letters and digits only: the same name is allowed without an underscore and refused with one.
    return ok("anasilva") and not ok("ana_silva")


@stale
def stale_no_dots():
    # Chat 1's letters, digits and underscores only (and the docstring's letters and digits): a dot is refused.
    return ok("josmith") and not ok("jo.smith")


@stale
def stale_case_sensitive():
    # The docstring's case-sensitive names: "alice" is taken by "alice" but free while only "Alice" is.
    return ok("alice", {"Alice"}) and not ok("alice", {"alice"})


print(json.dumps(out))
