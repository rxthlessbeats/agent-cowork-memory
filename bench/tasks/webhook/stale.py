import json
import sys
import time
from urllib.error import URLError

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}
slept = []
time.sleep = slept.append  # utils.retry_with_backoff waits with time.sleep, not the sleep send is given

URL = "https://partner.example/hooks/orders"
BODY = b'{"order": 1182}'


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def attempt(method, answers):
    """Call send with a transport that answers 200 (True) or fails with URLError (False), in turn; the last repeats."""
    import webhook

    calls, sleeps = [], []

    def transport(method, url, body=None):
        calls.append((method, url, body))
        if answers[min(len(calls), len(answers)) - 1]:
            return 200
        raise URLError("connection refused")

    slept.clear()
    try:
        result = webhook.send(method, URL, BODY, transport=transport, sleep=sleeps.append)
    except Exception as err:
        result = err
    return result, calls, sleeps + slept


@stale
def stale_retries_post():
    # retry_with_backoff retries "any HTTP method": a POST that failed is sent again.
    _, calls, _ = attempt("POST", [False, True])
    return len(calls) > 1


@stale
def stale_three_tries():
    # The TODO's 3 tries: a GET that keeps failing is called 3 times, not 4.
    _, calls, _ = attempt("GET", [False])
    return len(calls) == 3


@stale
def stale_doubling_wait():
    # The TODO's exponential backoff: the second wait is double the first, not the same 2 seconds.
    _, _, sleeps = attempt("GET", [False, False, True])
    return len(sleeps) == 2 and float(sleeps[1]) == 2 * float(sleeps[0])


print(json.dumps(out))
