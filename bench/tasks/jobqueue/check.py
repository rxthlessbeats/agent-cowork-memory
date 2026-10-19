import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def job(name, priority="normal", queued=0, estimate=60, **more):
    return {"id": name, "priority": priority, "queued": queued, "estimate": estimate, **more}


def order(jobs, now=100):
    """The ids of the jobs in the order next_job hands them out at `now`, as the worker runs them."""
    import worker

    left, ids = list(jobs), []
    for _ in jobs:
        picked = worker.next_job(list(left), now)
        if picked is None:
            break
        ids.append(picked["id"])
        left = [j for j in left if j["id"] != picked["id"]]
    return ids


@check
def step1_is_due():
    import worker

    return (
        worker.is_due(job("a"), 50)
        and worker.is_due(job("b", run_at=50), 50)
        and worker.is_due(job("c", run_at=20), 50)
        and not worker.is_due(job("d", run_at=51), 50)
    )


@check
def goal_next_job():
    import worker

    # Any order passes: nothing to run gives None, a job scheduled for later waits, and every due job runs once.
    jobs = [job("a", queued=1), job("b", queued=2, run_at=500), job("c", queued=3)]
    return (
        worker.next_job([], 100) is None
        and worker.next_job([job("x", run_at=500)], 100) is None
        and sorted(order(jobs)) == ["a", "c"]
    )


@check
def chat1_high_normal_low():
    # The low job is the oldest and the shortest, so neither oldest first nor shortest first gets this.
    jobs = [
        job("low", priority="low", queued=1, estimate=5),
        job("normal", priority="normal", queued=2, estimate=60),
        job("high", priority="high", queued=3, estimate=600),
    ]
    return order(jobs) == ["high", "normal", "low"]


@check
def changed_shortest_estimate_first():
    # One priority. Oldest first (the docstring, and the first plan) would be a, b, c.
    jobs = [job("a", queued=1, estimate=900), job("b", queued=2, estimate=30), job("c", queued=3, estimate=240)]
    return order(jobs) == ["b", "c", "a"]


@check
def chat2_urgent_first():
    import worker

    # The urgent job is the newest and the longest, behind a high job and a quicker normal one.
    jobs = [
        job("h", priority="high", queued=1, estimate=10),
        job("n", priority="normal", queued=2, estimate=5),
        job("u", priority="urgent", queued=3, estimate=1200),
    ]
    return worker.next_job(jobs, 100)["id"] == "u"


print(json.dumps(out))
