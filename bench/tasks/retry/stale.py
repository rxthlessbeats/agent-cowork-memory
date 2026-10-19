import io
import json
import sys
from urllib.error import HTTPError

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
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


def calls_for(codes):
    """How many calls fetch makes against a server answering with these status codes (the last one repeats)."""
    import client

    calls = []

    def opener(url, *args, **kwargs):
        calls.append(url)
        code = codes[min(len(calls), len(codes)) - 1]
        if code == 200:
            return Response()
        raise HTTPError(str(url), code, "error", {}, io.BytesIO(b""))

    try:
        client.fetch("http://vendor.test", opener=opener, sleep=lambda s: None)
    except Exception:
        pass
    return len(calls)


@stale
def stale_retries_other_errors():
    # "Retry only on HTTP 429 and 503; any other error is raised at once": another server or client error is tried again.
    return any(calls_for([code, 200]) > 1 for code in (500, 502, 504, 404))


print(json.dumps(out))
