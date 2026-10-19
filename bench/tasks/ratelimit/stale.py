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


def request(user="u1", key="k1", time=0.0):
    headers = {"X-Api-Key": key} if key is not None else {}
    return {"user": user, "path": "/", "headers": headers, "time": time}


@stale
def stale_per_user():
    # The README's rule limits a user: after u1 spends key a, u1's fresh key b is refused, though key b is unused.
    import limiter

    lim = limiter.Limiter()
    for _ in range(150):
        lim.allow(request(user="u1", key="a", time=1.0))
    return not lim.allow(request(user="u1", key="b", time=2.0))


@stale
def stale_60_per_minute():
    # The README's 60: the 61st request in a minute is refused, where 100 are allowed.
    import limiter

    lim = limiter.Limiter()
    return not all(lim.allow(request(time=1.0)) for _ in range(61))


@stale
def stale_admin_limited():
    # "Limits apply to everyone": an admin- key is refused somewhere in 200 requests.
    import limiter

    lim = limiter.Limiter()
    return not all(lim.allow(request(key="admin-ops", time=5.0)) for _ in range(200))


print(json.dumps(out))
