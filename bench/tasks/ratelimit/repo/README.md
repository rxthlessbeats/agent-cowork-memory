# API

`api.handle(request)` answers a request: a dict with `user`, `path`, `headers`, and `time` (seconds).

## Rate limits

Each user may make at most 60 requests per minute; anything over that gets status 429. Limits apply to everyone.
