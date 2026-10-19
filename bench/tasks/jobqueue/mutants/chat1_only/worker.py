"""The background worker's job queue.

A job is a dict: "id"; "priority", one of "high", "normal" or "low"; "queued", when it was queued (seconds);
"estimate", how many seconds it should take; and "run_at" (seconds), only on a job scheduled for later.

Jobs run oldest first, in the order they were queued: plain FIFO. Priority and estimate are only shown on the
dashboard; they never change the order.
"""

PRIORITIES = ["high", "normal", "low"]


def is_due(job, now):
    """Whether the job can run at time `now`: it has no run_at, or its run_at has come."""
    return job.get("run_at") is None or job["run_at"] <= now


def next_job(jobs, now):
    """Chat 1's order only: high, normal, low, and within a priority the oldest first; no urgent."""
    due = [job for job in jobs if is_due(job, now)]
    return min(due, key=lambda job: (PRIORITIES.index(job["priority"]), job["queued"]), default=None)


def run_all(jobs, now, run):
    """Run every job that can run at time `now`, one at a time, in the order next_job picks them."""
    waiting = list(jobs)
    while (job := next_job(waiting, now)) is not None:
        run(job)
        waiting.remove(job)
