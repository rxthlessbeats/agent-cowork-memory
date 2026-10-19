Let's do TASK.md in two steps, but the docstring in reminders.py is out of date on when reminders go out, so go by what I say here. I'll update the docstring myself later, so leave it as it is.

Step 1: make parse_appointment cope with what the front desk types: strip the spaces around each field, and keep only the digits of the phone number, so ` 2026-03-04 15:00 ; Sam Patel ; 0712-345 678 ` gives the name `Sam Patel` and the phone `0712345678`.

Step 2, for later: `reminder_times(appointment)`. One reminder 24 hours before wasn't enough, so the clinic wants two now: one 48 hours before, which leaves time to give the slot to someone else, and one 2 hours before. And patients complained about texts at night, so none may go out in the quiet hours, 22:00 to 07:00: a reminder that would fall in them goes out at 21:00 the evening before instead. So the 2-hour reminder for an 08:00 appointment goes out at 21:00 the night before.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how parse_appointment works now, line by line, and what could still go wrong with lines from the export: a missing field, an extra semicolon, a date in another format, and so on. Don't change anything.

---

Add an example of its output to message's docstring.

---

Add a test file, test_reminders.py, using unittest, for step 1: a clean line, a line with spaces around the fields, and a phone number with spaces and dashes.

---

Explain in detail how datetime.strptime and strftime differ, and which of their format codes depend on the locale. Don't change the code.

---

Explain in detail how SMS length limits work, GSM-7 against UCS-2, and what a name like "Zoë" or "Łukasz" does to the length of message's text. Don't change anything.

---

In parse_appointment, rename `when` to `start_text`, without changing behaviour.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in reminders.py right now, with an example call and its result.

---

Add `first_name(appointment)`: the first word of the patient's name. Use it in message so the text starts "Hi Sam,", and add a test for it.

---

Explain in detail how you would read the export with the csv module instead of splitting on semicolons, and what that would fix. Don't implement it.

---

Explain in detail how you would check that a phone number is a plausible UK mobile number, and what to do with foreign numbers. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
