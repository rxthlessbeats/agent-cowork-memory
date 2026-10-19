import json
import sys
import time

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def make():
    """A RateLimiter on a fake clock, and that clock."""
    import limiter

    clock = Clock()
    return limiter.RateLimiter(clock=clock), clock


def drain(lim, key):
    """Call allow until it says no (at most 100 times); return how many calls went through."""
    for n in range(100):
        if not lim.allow(key):
            return n
    return 100


@check
def step1_clock_param():
    import limiter

    lim, clock = make()
    return lim.clock is clock and limiter.RateLimiter().clock is time.monotonic and lim.allow("a")


@check
def goal_limits():
    lim, _ = make()
    return 0 < drain(lim, "a") < 100


@check
def chat_burst_of_8():
    lim, _ = make()
    return drain(lim, "a") == 8


@check
def chat_refill_every_1_5s():
    lim, clock = make()
    drain(lim, "a")
    clock.now = 1001.4
    if lim.allow("a"):
        return False
    clock.now = 1001.6
    return lim.allow("a") and not lim.allow("a")


@check
def chat_internal_unlimited():
    lim, _ = make()
    return drain(lim, "internal-reports") == 100 and drain(lim, "reports") < 100


print(json.dumps(out))
