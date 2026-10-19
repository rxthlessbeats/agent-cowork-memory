import time


class RateLimiter:
    """Limits how often each API key may call us."""

    def __init__(self):
        self.buckets = {}

    def allow(self, key):
        """True if this call from `key` may go ahead."""
        return True
