"""Rate limiting for api.handle, as README.md says: 60 requests per user per minute, for everyone."""

from collections import defaultdict, deque


def key_of(request):
    return request.get("headers", {}).get("X-Api-Key")


class Limiter:
    def __init__(self):
        self.seen = defaultdict(deque)

    def allow(self, request):
        now = request["time"]
        times = self.seen[request["user"]]
        while times and times[0] <= now - 60.0:
            times.popleft()
        if len(times) >= 60:
            return False
        times.append(now)
        return True
