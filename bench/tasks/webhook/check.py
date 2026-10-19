import json
import sys
import time
from urllib.error import URLError

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}
slept = []
time.sleep = slept.append  # a send that waits with time.sleep, not the sleep it was given, still runs at once

URL = "https://partner.example/hooks/orders"
BODY = b'{"order": 1182}'


def check(fn):
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


@check
def step1_transport():
    result, calls, sleeps = attempt("POST", [True])
    return result == 200 and calls == [("POST", URL, BODY)] and sleeps == []


@check
def goal_retries():
    result, calls, _ = attempt("GET", [False, True])
    return result == 200 and len(calls) == 2


@check
def chat_only_get_head():
    post, post_calls, _ = attempt("POST", [False, True])
    put, put_calls, _ = attempt("PUT", [False, True])
    head, head_calls, _ = attempt("HEAD", [False, True])
    return (
        isinstance(post, Exception)
        and len(post_calls) == 1
        and isinstance(put, Exception)
        and len(put_calls) == 1
        and head == 200
        and len(head_calls) == 2
    )


@check
def chat_four_attempts():
    result, calls, _ = attempt("GET", [False])
    return isinstance(result, Exception) and len(calls) == 4


@check
def chat_fixed_2s():
    result, _, sleeps = attempt("GET", [False, False, True])
    return result == 200 and [float(s) for s in sleeps] == [2.0, 2.0]


print(json.dumps(out))
