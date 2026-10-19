"""Helpers shared by the webhook code."""

import functools
import time


def retry_with_backoff(tries=3, delay=1.0):
    """Retry a call that fails with OSError, for any HTTP method: up to `tries` calls in all, waiting
    `delay` seconds after the first failure and doubling the wait after each one after that."""

    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            wait = delay
            for _ in range(tries - 1):
                try:
                    return fn(*args, **kwargs)
                except OSError:
                    time.sleep(wait)
                    wait *= 2
            return fn(*args, **kwargs)

        return wrapper

    return decorate
