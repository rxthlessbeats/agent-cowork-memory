Let's do TASK.md in two steps, but the README and settings.py are out of date on how times are shown, so go by what I say here. I'll update both myself later, so leave them as they are.

Step 1: `parse_time` gives a naive datetime for a start without an offset, like `2027-01-15T20:30` in events.csv, and then `upcoming` fails comparing it with the aware ones. Make it always return an aware datetime: a start without an offset is in UTC, which is what the box office exports.

Step 2, for later: `fmt(dt)`. Most of our audience is in Portugal now, so show times in Lisbon time, not UTC: Europe/Lisbon through zoneinfo, so summer time comes out right. Keep the 24-hour clock, but write the date day first with dots, the way the printed tickets do: 23:00 UTC on New Year's Eve shows as `31.12.2026 23:00`.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how parse_time works now, and how Python compares naive and aware datetimes: when it raises, and when it quietly gives an answer you might not expect. Don't change anything.

---

Add a docstring to `upcoming` saying what it returns, in what order, and whether an event starting exactly at `now` counts.

---

Add a test file, test_times.py, using unittest, for step 1: a start without an offset, one ending in Z, and one with +02:00.

---

Explain in detail how csv.reader handles titles with commas or quotes in them, and what events.csv must look like for them to load. Don't change the code.

---

Explain in detail what ISO 8601 allows that datetime.fromisoformat still rejects in Python 3.12, with examples. Don't change anything.

---

In events.load, replace the list comprehension with a plain for loop that appends each event, without changing behaviour.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in events.py and times.py right now, with an example call and its result.

---

Add `next_event(events, now)` to events.py: the first upcoming event, or None when there isn't one, with a test for it.

---

Explain in detail how you would load events from a JSON file as well as from CSV, choosing by the file's extension. Don't implement it.

---

Explain in detail how sorted keeps events that start at the same moment in their original order, and whether upcoming relies on that. Don't change anything.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
