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


def ok(name, taken=()):
    import validators

    return bool(validators.valid_username(name, set(taken)))


@check
def step1_valid_email():
    import validators

    return (
        validators.valid_email("ana@example.com")
        and not validators.valid_email("ana smith@example.com")
        and not validators.valid_email("ana@@example.com")
        and not validators.valid_email("ana@mail@example.com")
    )


@check
def goal_username():
    return ok("alice2026") and not ok("bad name!") and not ok("carol", {"carol", "dave"})


@check
def chat1_min_4():
    return not ok("abc") and ok("abcd")


@check
def chat1_underscore():
    return ok("ana_silva") and not ok("ana-silva")


@check
def chat1_unique_ignoring_case():
    return not ok("alice", {"Alice"}) and not ok("BOB", {"bob"}) and ok("alice", {"bob"})


@check
def changed_max_24():
    # 24 letters: too long for the docstring's 20 and for chat 1's 16.
    return ok("abcdefghijklmnopqrstuvwx") and not ok("abcdefghijklmnopqrstuvwxy")


@check
def chat2_dots():
    return ok("jo.smith") and not ok("jo/smith")


print(json.dumps(out))
