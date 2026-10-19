"""A small todo list.

Each todo is a dict with a title, a priority ("low", "normal" or "high"),
an optional due date and a done flag. The agenda goes by due date, earliest
first; priority only breaks ties.
"""
from datetime import timedelta

PRIORITIES = ("low", "normal", "high")
UNDATED_DUE = timedelta(days=7)  # a todo with no due date counts as due this long after today


def add(todos, title, priority="normal", due=None):
    if priority not in PRIORITIES:
        raise ValueError(f"unknown priority: {priority}")
    todos.append({"title": title, "priority": priority, "due": due, "done": False})
    return todos[-1]


def complete(todos, title):
    for todo in todos:
        if todo["title"] == title:
            todo["done"] = True
            return todo
    raise KeyError(title)


def overdue(todos, today):
    """Titles of the open todos due before today, in list order; a todo with no due date is never overdue."""
    titles = []
    for todo in todos:
        if not todo["done"] and todo["due"] is not None and todo["due"] < today:
            titles.append(todo["title"])
    return titles


def agenda(todos, today):
    """Titles of the open todos in the order to work on them: earliest due date first, then high, normal, low.
    Low-priority todos are left out unless they're overdue."""

    def due(todo):
        return today + UNDATED_DUE if todo["due"] is None else todo["due"]

    chosen = [t for t in todos if not t["done"] and not (t["priority"] == "low" and due(t) >= today)]
    # Two stable sorts: by priority first, then by due date, so priority only decides between equal due dates.
    chosen.sort(key=lambda t: PRIORITIES.index(t["priority"]), reverse=True)
    chosen.sort(key=due)
    return [t["title"] for t in chosen]
