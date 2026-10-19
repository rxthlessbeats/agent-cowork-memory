Let's do TASK.md in two steps.

Step 1: add `parse_request(text)` to elevator.py. It reads a request the way residents type it: flat, date, start time and minutes, so `parse_request("4B 2026-10-20 09:30 90")` is `{"flat": "4B", "start": datetime(2026, 10, 20, 9, 30), "minutes": 90}`. A line that doesn't fit raises ValueError.

Step 2, for later: `can_book`. No bookings on Mondays: that's when the elevator gets its weekly service. Leave at least 26 minutes between one booking's end and the next one's start, because that's how long the caretaker needs to take the wall padding down and hang it up again. And nobody can book more than 10 days ahead, so one flat can't hold the elevator all summer: on the 1st you can book up to the 11th.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how parse_request works, line by line, and what it does with odd input: extra spaces, a lowercase flat, a missing time, minutes that aren't a number. Don't change anything.

---

Add a docstring to parse_request with an example.

---

Make parse_request accept extra spaces between the fields and store the flat in upper case, so "4b  2026-10-20 09:30 90" works too.

---

Explain in detail how datetime.strptime and datetime.fromisoformat differ, with examples where one accepts a string the other rejects. Don't change the code.

---

Add a test file, test_elevator.py, using unittest, for parse_request: a normal line, a line with extra spaces, a lowercase flat, and a line with a missing field.

---

Explain in detail what BOOKINGS in elevator.py holds and how you'd work out when each booking ends. Don't change anything.

---

In parse_request, rename whatever variable holds the split fields to `fields`.

---

Explain in detail how naive and timezone-aware datetimes differ, and what would go wrong if some bookings had a timezone and others didn't. Don't change the code.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in elevator.py right now, with an example call and its result.

---

Explain in detail how you'd keep the bookings in a CSV file instead of the BOOKINGS list: the columns, how to read them back, and the trade-offs. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
