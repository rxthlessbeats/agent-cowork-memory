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


def recipe(serves, **ingredients):
    return {"serves": serves, "ingredients": ingredients}


@stale
def stale_min_10_guests():
    # The first plan's smallest batch, which the chat raised to 12: 3 guests get what 10 do, less than 12 get.
    import recipes

    batch = recipe(4, flour=(500, "g"))

    def flour(guests):
        return recipes.scale(batch, guests)["flour"][0]

    return flour(3) == flour(10) < flour(12)


print(json.dumps(out))
