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


LONG = "The quick brown fox jumps over the lazy dog and keeps on running far away"
FULL = "the-quick-brown-fox-jumps-over-the-lazy-dog-and-keeps-on-running-far-away"


def whole(slug):
    """A prefix of the full slug that ends where a word ends."""
    return FULL.startswith(slug) and FULL[len(slug)] == "-"


@check
def step1_slugify():
    import blog

    return blog.slugify("Café Déjà Vu!") == "cafe-deja-vu" and blog.slugify("  Hello,   World ") == "hello-world"


@check
def chat_unique_slug():
    import blog

    taken = blog.unique_slug("Hello World", {"hello-world"})
    return blog.unique_slug("Hello World", set()) == "hello-world" and isinstance(taken, str) and taken != "hello-world"


@check
def chat_numbered():
    import blog

    return (
        blog.unique_slug("Hello World", {"hello-world"}) == "hello-world-2"
        and blog.unique_slug("Hello World", {"hello-world", "hello-world-2"}) == "hello-world-3"
    )


@check
def chat_max_40():
    import blog

    first = blog.unique_slug(LONG, set())
    second = blog.unique_slug(LONG, {first})
    return len(first) <= 40 and whole(first) and len(second) <= 40 and second.endswith("-2") and whole(second[:-2])


print(json.dumps(out))
