Let's do TASK.md in two steps.

Step 1: add `parse(seat)` to seating.py: split a seat like "C7" into its row and number, `("C", 7)`. Raise ValueError for anything that isn't a seat in our auditorium, like "J4", "C13", "C0" or "7C".

Step 2, for later: `assign(guests, taken)`, with the venue's rules. Whatever the module docstring says, we seat people from the back now: row H first, then G and so on, each row from seat 1 up, guests in list order. Seat 7 in every row is behind a pillar, so never give it to anyone. And keep row D free for the board.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how seating.py works today, function by function, and what could go wrong with the data it gets: seats in lowercase, a taken set with seats that don't exist, two guests with the same name, and so on. Don't change anything.

---

Add a docstring to parse with a couple of examples.

---

Change of plan for step 2: the board wants to sit further back this year, so keep row F free for them, not row D. Still don't start step 2.

---

Explain in detail how str.isdigit, str.isdecimal and int() behave on inputs like "C05", "C 5", "C+5" and "C٥" (an Arabic-Indic five), and which of them parse accepts today. Don't change the code.

---

Add a test file, test_seating.py, using unittest, for parse: a normal seat, the last seat in the hall, and the bad seats "J4", "C13", "C0" and "7C".

---

Explain in detail why `seat not in taken` is slow when taken is a list and fast when it's a set, and how big the auditorium would have to be before that matters. Don't change anything.

---

In free_seats, rename the variable `seat` to `candidate`.

---

Explain in detail how you would read the taken seats from the ticketing system's CSV export, which has the row and the number in separate columns. Don't implement it.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in seating.py right now, with an example call and its result.

---

Explain in detail what the f-string in label does, and how a format spec like `:02d` on the number would change the seat labels and what it would break. Don't change anything.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
