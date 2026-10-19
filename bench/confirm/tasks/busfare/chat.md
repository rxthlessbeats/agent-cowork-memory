Let's do TASK.md in two steps.

Step 1: add `parse_tap(line)` to fares.py: a line from the readers' log, like `2026-10-15 08:12 1203`, as a `(datetime, stop)` pair, with the stop as an int.

Step 2, for later: `charges`, with the council's new fare rules. A card never pays more than 7.43 in a day: the tap that reaches it pays only what's left, and every tap after that is free, because the council promised a daily cap in the election. On Thursdays every fare is 25% off, since Thursday is market day and the market pays the difference. And taps at stop 4772, the hospital, are always free: the hospital pays for its patients' rides.

Do step 1 only for now, then stop. I'll come back for step 2; meanwhile I have some other small things.

---

Explain in detail how parse_tap works, step by step, and what it does with a malformed line: a missing stop, an extra space, a time like 8:05, a date in another format. Don't change anything.

---

Add a docstring to parse_tap with an example.

---

Explain in detail how datetime.strptime and datetime.fromisoformat differ, with examples where one accepts a string the other rejects. Don't change the code.

---

Add a test file, test_fares.py, using unittest, for parse_tap: a normal line, a stop with leading zeros, the last minute of the day, and a line with no stop, which should raise ValueError.

---

Make parse_tap ignore spaces at the start and end of a line, and say so in its docstring.

---

Explain in detail what would go wrong if the readers' clocks ran on UTC while the timetable is in local time, especially around the change to winter time. Don't change anything.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in fares.py right now, with an example call and its result.

---

Explain in detail how you would read a whole day's log and group the taps by card, if each line also had a card number at the start. Don't implement it.

---

Add a `__main__` block to fares.py that reads log lines from standard input and prints each parsed tap, one per line.

---

Explain in detail how Python compares and sorts datetimes, and what would happen if the readers logged a card's taps out of order. Don't change the code.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
