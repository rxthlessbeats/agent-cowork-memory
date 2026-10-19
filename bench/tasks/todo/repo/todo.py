"""A small todo list.

Each todo is a dict with a title, a priority ("low", "normal" or "high"),
an optional due date and a done flag. Priority decides what to work on first.
"""

PRIORITIES = ("low", "normal", "high")


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
