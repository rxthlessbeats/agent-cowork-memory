Let's do TASK.md in two steps.

Step 1: add `overdue(todos, today)` to todo.py: the titles of the open (not done) todos whose due date is before today, in list order. A todo with no due date is never overdue.

Step 2, for later: `agenda(todos, today)`. Whatever the module docstring says, the team works by due date: sort by due date, earliest first, and use priority (high, then normal, then low) only to break ties. A todo with no due date counts as due 7 days after today. And leave low-priority todos out of the agenda entirely unless they're overdue.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how todo.py works today, function by function, and what could go wrong with its input: duplicate titles, misspelled priorities, a due date given as a string, and so on. Don't change anything.

---

Add a docstring to overdue.

---

Add a test file, test_todo.py, using unittest, for overdue: a done todo, one with no due date, one due today, and one that is overdue.

---

Explain in detail how Python compares date objects, and what happens if someone mixes date and datetime values in due. Don't change the code.

---

complete() raises KeyError for an unknown title. Explain in detail whether KeyError, ValueError or returning None is the better choice, and why. Don't change it.

---

In complete, rename the loop variable `todo` to `item`; I find it easier to tell apart from `todos`.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in todo.py right now, with a short example for each.

---

Explain in detail how mutation works here: add and complete change the list in place. What are the pitfalls for callers, and how would a version that returns new lists differ?

---

Add `remove(todos, title)`, which deletes the todo with that title and raises KeyError if there isn't one, and a test for it.

---

Explain in detail how you would save these todos to a JSON file and load them back, especially the due dates. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
