"""Rate limiting: 100 requests per API key in any rolling 60 seconds, admin keys included."""

from collections import defaultdict, deque


def key_of(request):
    return request.get("headers", {}).get("X-Api-Key")


class Limiter:
    def __init__(self):
        self.seen = defaultdict(deque)

    def allow(self, request):
        key = key_of(request)
        if key is None:
            return False
        now = request["time"]
        times = self.seen[key]
        while times and times[0] <= now - 60.0:
            times.popleft()
        if len(times) >= 100:
            return False
        times.append(now)
        return True
