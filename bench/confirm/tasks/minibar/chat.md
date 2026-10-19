Let's do TASK.md in two steps.

Step 1: add `parse(line)` to minibar.py for the minibar's log lines: `parse("2026-05-05 21:14 out cola")` is `(datetime(2026, 5, 5, 21, 14), "out", "cola")`.

Step 2, for later: `bill`. Anything out of the minibar for more than 106 minutes is charged, even if it comes back, because by then it's warm and we can't sell it; anything back within 106 minutes isn't charged. Every item we charge for gets a 0.77 restocking fee on top, since someone has to carry a new one up. But no restocking fee on items taken out on a Sunday: housekeeping restocks every room on Sundays anyway.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how minibar.py works today, function by function, and what could go wrong with the log lines it gets: a blank line, an item that isn't in PRICES, two spaces in a row, and so on. Don't change anything.

---

Add a docstring to parse with an example.

---

Explain in detail how datetime.strptime and datetime.fromisoformat differ for lines like ours, with examples. Don't change the code.

---

Add a test file, test_minibar.py, using unittest, for parse: an "out" line, an "in" line, and a line from just before midnight.

---

Explain in detail what happens when two lines in a log have the same minute, and whether their order could ever matter. Don't change anything.

---

Make parse raise a ValueError that quotes the line when it doesn't have exactly four parts.

---

Explain in detail how PRICES could be loaded from a CSV file instead of living in the code, and the trade-offs. Don't implement it.

---

Write a NOTES.md with a "Functions" section describing each function in minibar.py that works today, with an example call and its result. Leave out anything that isn't built yet.

---

Explain in detail how Python compares naive and aware datetimes, and what would break if the sensors logged in UTC. Don't change the code.

---

Add type hints to parse.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
