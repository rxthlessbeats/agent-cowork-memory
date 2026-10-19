Let's do TASK.md in two steps.

Step 1: add `headcount(replies)` to catering.py: how many guests are coming, from the RSVP replies. A reply is "yes", "no", or "yes +N" for someone bringing N more people, so `["yes", "yes +2", "no"]` is 4. Anything else counts as nobody.

Step 2, for later: `servers`, `arrival` and `price`. One server for every 25 guests, rounded up, since that's what the venues ask for. The crew arrives 54 minutes before the start: that's how long the drive and setting up the buffet take. And events on a Sunday cost 33% more, because the agency charges us Sunday rates for the staff.

Do step 1 only for now, then stop. I'll come back for step 2; meanwhile I have some other small things.

---

Explain in detail how headcount works and what it does with replies like "YES", " yes +2 ", "yes+2", "yes +two" and an empty string. Don't change anything.

---

Add a docstring to headcount with an example.

---

Change of plan for step 2: one server for every 18 guests, not 25, still rounded up: our insurer wants more staff on the floor. Still don't start step 2.

---

Explain in detail how str.split, str.partition and a regular expression would each take "yes +2" apart, and which you'd trust with messy input. Don't change the code.

---

Add a test file, test_catering.py, using unittest, for headcount: an empty list, only noes, a plus-one, and a reply that is neither yes nor no.

---

Make headcount ignore spaces around each reply, and say so in its docstring.

---

Explain in detail how Python compares strings that look the same but are spelled with different Unicode characters, and whether that could matter for RSVP replies. Don't change anything.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in catering.py right now, with an example call and its result.

---

Explain in detail how you would read the replies from a CSV export of the RSVP form, with a name and a reply on each row. Don't implement it.

---

In headcount, rename the loop variable to `reply` if it's called something else.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
