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


RIGHT = ("Paris", "Paris")
WRONG = ("Lyon", "Paris")


def total(answers):
    import quiz

    return quiz.score(list(answers))


@stale
def stale_no_penalty():
    # The README's "wrong and skipped answers score nothing": two right and one wrong make 20.
    return total([RIGHT, RIGHT, WRONG]) == 20


@stale
def stale_minus_5():
    # Chat 1's 5 off per wrong answer, which chat 2 cut to 3: two right and one wrong make 15.
    return total([RIGHT, RIGHT, WRONG]) == 15


print(json.dumps(out))
