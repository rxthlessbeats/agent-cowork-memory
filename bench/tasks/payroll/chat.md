Let's do TASK.md in two steps.

Step 1: add `parse_hours(text)` to payroll/timesheet.py, as TASK.md says.

Before step 2 I need to know where overtime is really paid in this repo, because I never remember. There are two overtime.py files and I don't know which one runs. Find out and tell me: when something calls payroll.pay, which code pays the overtime, and how does pay get to it? What is the other overtime.py for? Also tell me the command that runs the tests.

Do step 1 and answer those, but don't start step 2: I'll come back for it later. Meanwhile I have some other small things.

---

Explain in detail how parse_hours handles unusual entries: "7:5", "7:60", "-1:30", " 8:00 ", "8h", "8" and an empty string, and what someone filling in a timesheet would expect for each. Don't change the code.

---

Add a docstring to format_hours with an example, and say what it does with a value like 7.999.

---

Add a test file, tests/test_timesheet.py, using unittest, for parse_hours and format_hours: a few entries each, and that format_hours(parse_hours(entry)) gives back "7:45" and "0:05".

---

Explain in detail how binary floating point affects hours like 7:20 or 0:05 once they're floats, with concrete numbers. Don't change the code.

---

Why do timesheets use hours and minutes while pay is worked out in decimal hours? Explain in detail, including the common mistake of reading 7.30 as seven and a half hours.

---

In format_hours, rename the local variable `minutes` to `total_minutes`, without changing behaviour.

---

Write a NOTES.md with a "Timesheet" section describing each public function in payroll/timesheet.py right now, with an example call and its result.

---

Add `total_hours(entries)` to payroll/timesheet.py: the hours in a list of entries like ["7:45", "8:00"], added up in whole minutes so no float error creeps in, and a test for it.

---

Explain in detail how you would support a shift written as a time range, like "22:00-06:00", that crosses midnight. Don't implement it.

---

Explain in detail the trade-offs of keeping hours as whole minutes (ints) instead of floats in the timesheet code. Don't change anything.

---

Explain in detail how unittest's assertAlmostEqual works, and when a test about hours should use it instead of assertEqual. Don't change anything.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
