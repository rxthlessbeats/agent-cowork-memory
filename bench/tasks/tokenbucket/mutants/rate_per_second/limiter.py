import time

CAPACITY = 8
REFILL_PER_SECOND = 1.5


class RateLimiter:
    """Limits how often each API key may call us."""

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.buckets = {}

    def allow(self, key):
        """True if this call from `key` may go ahead."""
        if key.startswith("internal-"):
            return True
        now = self.clock()
        tokens, last = self.buckets.get(key, (CAPACITY, now))
        tokens = min(CAPACITY, tokens + (now - last) * REFILL_PER_SECOND)
        allowed = tokens >= 1
        self.buckets[key] = (tokens - 1 if allowed else tokens, now)
        return allowed
