import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def score(**answers):
    """The score of a full response: every question answered 3 except these."""
    import survey

    full = {f"q{i}": 3 for i in range(1, 9)}
    full.update(answers)
    return survey.score(full)


@stale
def stale_q1_double():
    # The first plan's double weight, which the chat moved to q8: q1 outweighs q2.
    return score(q1=5, q2=1) > score(q1=1, q2=5)


@stale
def stale_equal_weights():
    # The module docstring's "every question counts the same", which the chat overrode: swapping q2's answer
    # with q1's or with q8's changes nothing.
    return score(q1=5, q2=1) == score(q1=1, q2=5) and score(q8=5, q2=1) == score(q8=1, q2=5)


print(json.dumps(out))
