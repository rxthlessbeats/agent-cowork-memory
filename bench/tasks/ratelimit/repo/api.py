"""A tiny API. A request is a dict: user, path, headers, time (seconds)."""


def handle(request, limiter=None):
    if limiter is not None and not limiter.allow(request):
        return {"status": 429}
    return {"status": 200, "body": f"hello {request['user']}"}
