Let's do TASK.md in two steps.

Step 1: add `minutes(session)` to parking.py: how long the car was parked, in whole minutes, where a started minute counts as a full one (9:00:00 to 9:10:01 is 11 minutes). Raise ValueError for a car that hasn't left yet.

Step 2, for later: `fee(session)`, with the garage's new rules. Whatever the module docstring says, we charge 80 cents for every started 20 minutes, not by the hour. Cars that came in on a Sunday park free. And no session costs more than 13.60, however long it is.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how parking.py works today, function by function, and what could go wrong with the sessions it gets: missing keys, a car that leaves before it came in, times given as strings, and so on. Don't change anything.

---

Change of plan for step 2: finance says 13.60 is less than the garage next door charges, so cap a session at 16.80, not 13.60. Still don't start step 2.

---

Add a docstring to minutes that says what it returns and when it raises ValueError.

---

Explain in detail how subtracting two datetimes works in Python: what a timedelta holds, why .seconds and .total_seconds() differ, and how that matters in minutes. Don't change the code.

---

Add a test file, test_parking.py, using unittest, for minutes: an exact number of minutes, a partial minute, a stay over midnight, and a car that hasn't left yet.

---

Explain in detail how naive and timezone-aware datetimes differ, what zoneinfo adds, and what would happen here if the barrier system started sending times in UTC. Don't change anything.

---

In still_parked and visits, rename the variable `s` to `stay`.

---

Explain in detail the trade-offs of raising ValueError for a car that hasn't left yet, compared with returning None or counting up to the current time, and how callers would handle each. Don't change it.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in parking.py right now, with an example call and its result.

---

Explain in detail how SESSIONS is structured and what would change if the sessions came from the barrier system's CSV export instead of being kept in code. Don't change anything.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
