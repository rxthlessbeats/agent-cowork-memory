Let's do TASK.md in two steps, but don't use `retry_with_backoff` from utils.py, whatever the TODO says. When billing used it, it retried a POST that had timed out on our side but gone through on the partner's, and a customer was charged twice. I'll take the decorator and the TODO out myself later, so leave utils.py as it is.

Step 1: make `send` take two keyword arguments, `transport` and `sleep`, so tests never touch the network or wait. `transport(method, url, body)` makes one call and returns the response status, or raises `OSError` when the call fails; the default one does the urlopen call that's in `send` now. `sleep` defaults to `time.sleep`. No retries yet.

Step 2, for later: the retries, in `send` itself. Retry only GET and HEAD; a POST, or any other method, is never retried. At most 4 attempts in total, a fixed 2 seconds apart. If every attempt fails, raise the last error.

Do step 1 only for now, then stop. I'll come back for step 2.
