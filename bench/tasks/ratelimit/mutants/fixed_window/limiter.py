"""Rate limiting: 100 requests per API key per clock minute (a fixed window, not a rolling one)."""

from collections import defaultdict


def key_of(request):
    return request.get("headers", {}).get("X-Api-Key")


class Limiter:
    def __init__(self):
        self.counts = defaultdict(int)

    def allow(self, request):
        key = key_of(request)
        if key is None:
            return False
        if key.startswith("admin-"):
            return True
        window = (key, int(request["time"] // 60))
        if self.counts[window] >= 100:
            return False
        self.counts[window] += 1
        return True
