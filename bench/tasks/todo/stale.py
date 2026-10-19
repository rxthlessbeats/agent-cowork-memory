import json
import sys
from datetime import date, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TODAY = date(2025, 6, 10)


def todo(title, priority="normal", days=None, done=False):
    due = None if days is None else TODAY + timedelta(days=days)
    return {"title": title, "priority": priority, "due": due, "done": done}


@stale
def stale_priority_first():
    # The module docstring's "Priority decides what to work on first": a high-priority todo due in 6 days comes
    # before a normal one due in 2, where the team goes by due date.
    import todo as module

    titles = module.agenda([todo("plan", "high", days=6), todo("fix", days=2)], TODAY)
    return titles.index("plan") < titles.index("fix")


print(json.dumps(out))
