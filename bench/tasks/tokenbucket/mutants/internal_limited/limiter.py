import time

CAPACITY = 8
REFILL_SECONDS = 1.5


class RateLimiter:
    """Limits how often each API key may call us."""

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.buckets = {}

    def allow(self, key):
        """True if this call from `key` may go ahead."""
        now = self.clock()
        tokens, last = self.buckets.get(key, (CAPACITY, now))
        tokens = min(CAPACITY, tokens + (now - last) / REFILL_SECONDS)
        allowed = tokens >= 1
        self.buckets[key] = (tokens - 1 if allowed else tokens, now)
        return allowed
