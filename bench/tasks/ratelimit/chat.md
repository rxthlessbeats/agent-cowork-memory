Let's do TASK.md in two steps, but the README is out of date on the limits, so go by what I say here. I'll update the README myself later, so leave it as it is.

Step 1: in limiter.py, add `key_of(request)`: the request's API key, from the `X-Api-Key` header, or None when there isn't one.

Step 2, for later: `class Limiter` with `allow(request)`, using the request's `time`. Limit by API key, not by user: several users share a key, and the key is what we bill. A request without a key is always refused. Each key gets 100 requests in any rolling 60 seconds. And keys that start with `admin-` are never limited.

Do step 1 only for now, then stop. I'll come back for step 2.
