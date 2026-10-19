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


def route(subject, body="", priority=3):
    import routing

    return routing.route({"subject": subject, "body": body, "email": "sam@customer.example", "priority": priority})


@stale
def stale_reads_body():
    # The docstring's "subject or body", which chat 1 overruled: a refund asked for only in the body goes to billing.
    return route("Question", "I would like a refund") == "billing"


print(json.dumps(out))
