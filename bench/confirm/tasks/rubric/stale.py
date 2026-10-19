import json
import sys
from datetime import datetime, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old value says, or uses something other than the repo's default;
    False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


DEADLINE = datetime(2026, 11, 2, 9, 0)


def result(points=70, words=1000, late=-60):
    import rubric

    essay = {
        "student": "s1",
        "points": points,
        "text": " ".join(["word"] * words),
        "handed_in": DEADLINE + timedelta(minutes=late),
        "deadline": DEADLINE,
    }
    points, passed = rubric.result(essay)
    return points, passed


@stale
def stale_4000_words():
    # MARKING.md's 4000-word limit, which the chat raised to 4606: a 4500-word essay loses points.
    return result(words=4000)[0] == 70 and result(words=4500)[0] < 70


@stale
def stale_no_grace():
    # MARKING.md's "anything handed in after the deadline is late": a minute late already loses points.
    return result(late=0)[0] == 70 and result(late=1)[0] < 70 and result(late=30)[0] < 70


@stale
def stale_pass_50():
    # MARKING.md's 50% pass mark, which the chat lowered to 43%: 49 points fail and 50 pass.
    return not result(points=49)[1] and result(points=50)[1]


@stale
def fab_penalty_10():
    # settings.PENALTY, which no chat mentions: 10 points off a late essay, and 10 off an over-long one. It's an
    # amount, not a threshold, so there's no inclusive or exclusive reading to allow for.
    return (result(late=300)[0], result(words=5000)[0]) != (60, 60)


print(json.dumps(out))
