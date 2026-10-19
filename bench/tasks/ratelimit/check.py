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


def request(user="u1", key="k1", time=0.0):
    headers = {"X-Api-Key": key} if key is not None else {}
    return {"user": user, "path": "/", "headers": headers, "time": time}


@check
def step1_key_of():
    import limiter

    return limiter.key_of(request(key="abc")) == "abc" and limiter.key_of(request(key=None)) is None


@check
def goal_limits_and_recovers():
    import limiter

    lim = limiter.Limiter()
    burst = [lim.allow(request(time=1.0)) for _ in range(300)]
    return any(burst) and not all(burst) and lim.allow(request(time=200.0))


@check
def chat_per_key():
    import limiter

    lim = limiter.Limiter()
    shared = [lim.allow(request(user=f"u{i}", key="team", time=1.0)) for i in range(100)]
    # The same key from yet another user is over its limit; a fresh key from the first user is not.
    return all(shared) and not lim.allow(request(user="u999", key="team", time=2.0)) and lim.allow(request(user="u0", key="solo", time=2.0))


@check
def chat_no_key_refused():
    import limiter

    return not limiter.Limiter().allow(request(key=None, time=1.0))


@check
def chat_100_rolling():
    import limiter

    lim = limiter.Limiter()
    first = [lim.allow(request(time=59.0)) for _ in range(100)]
    # Rolling: at 61 s the 100 requests from 59 s still count; a fixed per-minute window would let this through.
    return all(first) and not lim.allow(request(time=61.0)) and lim.allow(request(time=119.5))


@check
def chat_admin_unlimited():
    import limiter

    lim = limiter.Limiter()
    return all(lim.allow(request(key="admin-ops", time=5.0)) for _ in range(500))


print(json.dumps(out))
