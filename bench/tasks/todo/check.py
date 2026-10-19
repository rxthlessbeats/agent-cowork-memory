import json
import sys
from datetime import date, timedelta

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


TODAY = date(2025, 6, 10)


def todo(title, priority="normal", days=None, done=False):
    due = None if days is None else TODAY + timedelta(days=days)
    return {"title": title, "priority": priority, "due": due, "done": done}


@check
def step1_overdue():
    import todo as module

    todos = [
        todo("late", days=-3),
        todo("finished", days=-5, done=True),
        todo("someday"),
        todo("today", days=0),
        todo("later", days=4),
        todo("also late", "low", days=-1),
    ]
    return module.overdue(todos, TODAY) == ["late", "also late"]


@check
def goal_agenda():
    import todo as module

    todos = [todo("a", days=2), todo("b", "high", days=5), todo("c", done=True), todo("d")]
    return sorted(module.agenda(todos, TODAY)) == ["a", "b", "d"]


@check
def chat_due_date_first():
    import todo as module

    todos = [todo("urgent later", "high", days=10), todo("normal soon", days=1)]
    return module.agenda(todos, TODAY) == ["normal soon", "urgent later"]


@check
def chat_no_due_is_seven_days():
    import todo as module

    todos = [todo("in ten", days=10), todo("no date"), todo("in five", days=5)]
    return module.agenda(todos, TODAY) == ["in five", "no date", "in ten"]


@check
def chat_low_only_if_overdue():
    import todo as module

    todos = [todo("low soon", "low", days=3), todo("low late", "low", days=-2), todo("normal", days=4)]
    titles = module.agenda(todos, TODAY)
    return "low soon" not in titles and "low late" in titles and "normal" in titles


print(json.dumps(out))
