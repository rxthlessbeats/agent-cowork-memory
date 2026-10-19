"""Rate limiting for api.handle: per API key, 100 requests in any rolling 60 seconds; admin- keys unlimited."""

from collections import defaultdict, deque

LIMIT = 100
WINDOW = 60.0


def key_of(request):
    return request.get("headers", {}).get("X-Api-Key")


class Limiter:
    def __init__(self):
        self.seen = defaultdict(deque)

    def allow(self, request):
        key = key_of(request)
        if key is None:
            return False
        if key.startswith("admin-"):
            return True
        now = request["time"]
        times = self.seen[key]
        while times and times[0] <= now - WINDOW:
            times.popleft()
        if len(times) >= LIMIT:
            return False
        times.append(now)
        return True
