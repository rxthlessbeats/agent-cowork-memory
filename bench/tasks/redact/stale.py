import copy
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
def stale_changes_event():
    # "Never change the event that was passed in; work on a copy": the caller's event, nested parts too, comes back changed.
    import logs

    event = {
        "user": "ana",
        "password": "p",
        "api_key": "k",
        "card_number": "4111111111114242",
        "auth": {"token": "t"},
        "items": [{"password": "p"}, "plain"],
    }
    before = copy.deepcopy(event)
    logs.format_event(event)
    return event != before


print(json.dumps(out))
