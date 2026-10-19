Let's do TASK.md in two steps.

Step 1: give `RateLimiter` a `clock` parameter that defaults to `time.monotonic` and is kept as `self.clock`, so tests can pass a fake clock. `allow` keeps returning True for now.

Step 2, for later: the buckets, one per API key. Our gateway contract allows bursts of 8 calls, so a bucket holds 8 tokens and starts full. It refills one token every 1.5 seconds. Keys that start with `internal-` belong to our own services and are never limited.

Do step 1 only for now, then stop. I'll come back for step 2.
