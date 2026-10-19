Let's do TASK.md in two steps.

Step 1: add `clashes(bookings, room, start, end)` to booking.py: the bookings of that room that overlap the time from start to end, in list order. Bookings that only touch, where one ends exactly when the other starts, don't overlap.

Step 2, for later: `book(bookings, room, start, end)`, with the office rules. Whatever the module docstring says, leave at least 10 minutes between two bookings of the same room, for cleaning. Nothing may start before 8:30 or end after 17:45. And no booking may be longer than 90 minutes.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how booking.py works today, function by function, and what could go wrong with the bookings it gets: an unknown room, an end before the start, times on different days, and so on. Don't change anything.

---

Add a docstring to clashes that says what counts as an overlap.

---

Explain in detail how comparing datetimes works in Python, and what happens if someone mixes naive and timezone-aware datetimes in bookings. Don't change the code.

---

Add a test file, test_booking.py, using unittest, for clashes: no bookings at all, an overlap, two bookings that only touch, and a booking of another room.

---

Explain in detail how rooms_for picks and sorts the rooms, and what sorted with key=ROOMS.get does, step by step. Don't change it.

---

In bookings_of, rename the variable `b` to `booking`.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in booking.py right now, with an example call and its result.

---

Explain in detail how you would keep the bookings in SQLite instead of a list, including how datetimes are stored and compared there. Don't implement it.

---

Add type hints to the functions in booking.py without changing their behaviour.

---

Explain in detail what could go wrong if two people book through the bot at the same moment, and the usual ways to prevent double bookings. Don't change anything.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
