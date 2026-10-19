import io
import json
import sys
from urllib.error import HTTPError

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


class Response:
    def read(self):
        return b"ok"

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def attempt(codes):
    """Call fetch against a server answering with these status codes (the last one repeats)."""
    import client

    calls, sleeps = [], []

    def opener(url, *args, **kwargs):
        calls.append(url)
        code = codes[min(len(calls), len(codes)) - 1]
        if code == 200:
            return Response()
        raise HTTPError(str(url), code, "error", {}, io.BytesIO(b""))

    try:
        result = client.fetch("http://vendor.test", opener=opener, sleep=sleeps.append)
    except HTTPError as err:
        result = err
    return result, len(calls), sleeps


@check
def step1_sleep_param():
    return attempt([200]) == (b"ok", 1, [])


@check
def goal_retries():
    result, calls, _ = attempt([503, 200])
    return result == b"ok" and calls == 2


@check
def chat_only_429_503():
    r500, c500, _ = attempt([500])
    r404, c404, _ = attempt([404])
    r429, _, _ = attempt([429, 200])
    return isinstance(r500, HTTPError) and c500 == 1 and isinstance(r404, HTTPError) and c404 == 1 and r429 == b"ok"


@check
def chat_four_attempts():
    result, calls, _ = attempt([503])
    return isinstance(result, HTTPError) and result.code == 503 and calls == 4


@check
def chat_backoff():
    _, _, sleeps = attempt([429])
    return [float(s) for s in sleeps] == [0.5, 1.0, 2.0]


print(json.dumps(out))
