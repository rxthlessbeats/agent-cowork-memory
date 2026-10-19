import time

BURST = 8  # tokens a bucket holds, and starts with: the gateway contract's burst
REFILL_EVERY = 1.5  # seconds per token


class RateLimiter:
    """Limits how often each API key may call us."""

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.buckets = {}  # key -> [whole tokens left, time the next token is counted from]

    def allow(self, key):
        """True if this call from `key` may go ahead."""
        if key.startswith("internal-"):
            return True  # our own services
        now = self.clock()
        bucket = self.buckets.setdefault(key, [BURST, now])
        earned = max(0, int((now - bucket[1]) // REFILL_EVERY))
        if earned:
            bucket[0] = min(BURST, bucket[0] + earned)
            bucket[1] += earned * REFILL_EVERY
        if bucket[0] == BURST:
            bucket[1] = now  # a full bucket earns nothing while it waits
        if not bucket[0]:
            return False
        bucket[0] -= 1
        return True
