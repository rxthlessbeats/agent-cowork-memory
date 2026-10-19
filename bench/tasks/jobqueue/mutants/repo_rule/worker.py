"""The background worker's job queue.

A job is a dict: "id"; "priority", one of "high", "normal" or "low"; "queued", when it was queued (seconds);
"estimate", how many seconds it should take; and "run_at" (seconds), only on a job scheduled for later.

Jobs run oldest first, in the order they were queued: plain FIFO. Priority and estimate are only shown on the
dashboard; they never change the order.
"""


def is_due(job, now):
    """Whether the job can run at time `now`: it has no run_at, or its run_at has come."""
    return job.get("run_at") is None or job["run_at"] <= now


def next_job(jobs, now):
    """The due job queued first, as the module docstring says: plain FIFO, whatever the priority or estimate."""
    due = [job for job in jobs if is_due(job, now)]
    return min(due, key=lambda job: job["queued"], default=None)


def run_all(jobs, now, run):
    """Run every job that can run at time `now`, one at a time, in the order next_job picks them."""
    waiting = list(jobs)
    while (job := next_job(waiting, now)) is not None:
        run(job)
        waiting.remove(job)
