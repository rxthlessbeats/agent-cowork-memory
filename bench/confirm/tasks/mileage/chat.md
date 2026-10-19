Let's do TASK.md in two steps.

Step 1: add `parse_trip(line)` to mileage.py: a line from the expenses form, like `2026-03-05 84 6.50`, becomes a trip, `{"day": date(2026, 3, 5), "miles": 84, "parking": Decimal("6.50")}`. The parking is optional; without it, it's `Decimal("0")`.

Step 2, for later: `settle`, with the new expenses policy. The first 57 miles of every trip aren't paid, since that's about what everyone drives to the office and back anyway, so a trip of 57 miles or less pays no mileage at all. Parking is paid back up to 7.96 a trip, the day rate at the station car park; anything over that is on them. And a claim is paid on the first Thursday after it's submitted, because payroll closes on Wednesday night: a claim submitted on a Thursday waits a week.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how mileage.py works today, function by function, and what could go wrong with the claims it gets: miles given as a string, negative parking, a trip dated after the claim was submitted, and so on. Don't change anything.

---

Add a docstring to parse_trip with an example.

---

Change of plan for step 2: HR went through everyone's home address, and the usual drive to the office and back is 37 miles, not 57. So take the first 37 miles off each trip instead. Still don't start step 2.

---

Explain in detail how parse_trip handles a line without parking, extra spaces, and a comma instead of a dot in the parking, and where it could surprise someone. Don't change the code.

---

Add a test file, test_mileage.py, using unittest, for parse_trip: a line with parking, a line without, a line with extra spaces, and a line with a date that doesn't exist.

---

Explain in detail how the loop in total_miles compares with sum() over a generator expression, and when the difference would start to matter. Don't change anything.

---

In total_miles, rename the loop variable `trip` to `journey`.

---

Explain in detail how date.fromisoformat and datetime.strptime differ, with examples of dates one accepts and the other doesn't. Don't change the code.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in mileage.py right now, with an example call and its result.

---

Explain in detail what would change if the claims lived in a SQLite table instead of a Python list: the schema, what claims_by would look like as a query, and the trade-offs. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
