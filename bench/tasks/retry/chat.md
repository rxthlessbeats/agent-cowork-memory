Let's do TASK.md in two steps.

Step 1: give `fetch` a `sleep` parameter that defaults to `time.sleep`, so tests can pass a fake one and never wait. Nothing else changes yet.

Step 2, for later: the retries. The vendor told us to retry only on HTTP 429 and 503; any other error is raised at once. At most 4 attempts in total. Wait 0.5 s before the second attempt, then 1 s, then 2 s. If every attempt fails, raise the last error.

Do step 1 only for now, then stop. I'll come back for step 2.
