"""A small todo list.

Each todo is a dict with a title, a priority ("low", "normal" or "high"),
an optional due date and a done flag. Priority decides what to work on first.
"""
from datetime import timedelta

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


def overdue(todos, today):
    return [t["title"] for t in todos if not t["done"] and t["due"] is not None and t["due"] < today]


def agenda(todos, today):
    def due(t):
        return t["due"] if t["due"] is not None else today + timedelta(days=7)

    open_todos = [t for t in todos if not t["done"] and t["priority"] != "low"]
    open_todos.sort(key=lambda t: (due(t), -PRIORITIES.index(t["priority"])))
    return [t["title"] for t in open_todos]
