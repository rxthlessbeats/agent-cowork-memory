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


def load(env):
    import config

    return config.load(env)


@stale
def stale_true_false_bool():
    # "true and false stay strings": true is turned into a boolean like yes. (Not probed with false: debug's default
    # is already False, so a folder that ignores the variable would look the same.)
    return load({"MYAPP_DEBUG": "true"})["debug"] is True


@stale
def stale_adds_unknown_keys():
    # "Never add new keys to the config": a variable that matches no key adds one instead of raising.
    return "color" in {key.lower() for key in load({"MYAPP_COLOR": "red"})}


print(json.dumps(out))
