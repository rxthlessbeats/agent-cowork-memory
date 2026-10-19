"""The background worker's job queue.

A job is a dict: "id"; "priority", one of "high", "normal" or "low"; "queued", when it was queued (seconds);
"estimate", how many seconds it should take; and "run_at" (seconds), only on a job scheduled for later.

Jobs run oldest first, in the order they were queued: plain FIFO. Priority and estimate are only shown on the
dashboard; they never change the order.
"""


def next_job(jobs, now):
    """The job the worker should run next at time `now` (seconds), or None when no job can run yet."""
    raise NotImplementedError


def run_all(jobs, now, run):
    """Run every job that can run at time `now`, one at a time, in the order next_job picks them."""
    waiting = list(jobs)
    while (job := next_job(waiting, now)) is not None:
        run(job)
        waiting.remove(job)
