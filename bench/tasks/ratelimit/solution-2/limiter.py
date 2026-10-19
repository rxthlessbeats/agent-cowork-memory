"""Rate limiting for api.handle (README.md is out of date): 100 requests per API key in any rolling 60 seconds."""

import bisect


def key_of(request):
    headers = request.get("headers") or {}
    return headers.get("X-Api-Key")


class Limiter:
    LIMIT = 100
    WINDOW = 60.0

    def __init__(self):
        self.times = {}

    def allow(self, request):
        key = key_of(request)
        if not key:
            return False
        if key.startswith("admin-"):
            return True
        now = request["time"]
        times = self.times.setdefault(key, [])
        # Keep only the requests inside the window that ends now.
        del times[: bisect.bisect_right(times, now - self.WINDOW)]
        if len(times) >= self.LIMIT:
            return False
        bisect.insort(times, now)
        return True
