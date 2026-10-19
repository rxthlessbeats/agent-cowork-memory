Let's do TASK.md in two steps, but the docstring in worker.py is out of date on the order, so go by what I say here. I'll update the docstring myself later, so leave it as it is.

Step 1: in worker.py, add `is_due(job, now)`: True when the job can run at time `now`, meaning it has no `run_at` or its `run_at` is at or before `now`. Nothing else changes yet.

Step 2, for later: `next_job(jobs, now)` picks from the jobs that are due, by priority: high before normal before low, so password resets stop waiting behind the nightly exports. Within a priority, the oldest job goes first.

Do step 1 only for now, then stop. I'll come back for step 2.
