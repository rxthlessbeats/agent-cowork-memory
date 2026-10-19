"""The background worker's job queue.

A job is a dict: "id"; "priority", one of "high", "normal" or "low"; "queued", when it was queued (seconds);
"estimate", how many seconds it should take; and "run_at" (seconds), only on a job scheduled for later.

Jobs run oldest first, in the order they were queued: plain FIFO. Priority and estimate are only shown on the
dashboard; they never change the order.
"""

RANK = {"urgent": 0, "high": 1, "normal": 2, "low": 3}


def is_due(job, now):
    """Whether the job can run at time `now`: it has no run_at, or its run_at is at or before now."""
    return "run_at" not in job or job["run_at"] <= now


def next_job(jobs, now):
    """The job the worker should run next at time `now` (seconds), or None when no job can run yet.

    By priority (urgent, high, normal, low), and within a priority the shortest estimate first.
    """
    due = sorted((job for job in jobs if is_due(job, now)), key=lambda job: (RANK[job["priority"]], job["estimate"]))
    return due[0] if due else None


def run_all(jobs, now, run):
    """Run every job that can run at time `now`, one at a time, in the order next_job picks them."""
    waiting = list(jobs)
    while (job := next_job(waiting, now)) is not None:
        run(job)
        waiting.remove(job)
