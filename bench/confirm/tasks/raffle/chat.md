Let's do TASK.md in two steps.

Step 1: add `tickets_held(draw, buyer)` to raffle.py: how many tickets that buyer already has for the draw, matching names without caring about upper or lower case or extra spaces, so "ana  SILVA" finds Ana Silva's tickets. Someone with none has 0.

Step 2, for later: `can_buy(draw, buyer, count, now)`, with the club's limits. Nobody may hold more than 58 tickets for one draw, counting the ones they already have: that's the cap in our gaming licence. A draw never has more than 3580 tickets in total, because that's how many numbered tickets the printer makes for each draw. And a sale has to be at least 30 minutes before the draw, so the stubs can be counted.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how raffle.py works today, function by function, and what could go wrong with the draws it gets: a buyer's name spelled two ways, a negative ticket count, a draw time that's only a date, and so on. Don't change anything.

---

Add a docstring to tickets_held with an example.

---

Change of plan for step 2: the auditor now counts the stubs before the draw starts and needs longer, so a sale has to be at least 65 minutes before the draw, not 30. Still don't start step 2.

---

Explain in detail how tickets_held compares names: what str.lower, str.casefold and str.split do with names like "Zoë", "Straße" or a name with a tab in it, and where it could surprise someone. Don't change the code.

---

Add a test file, test_raffle.py, using unittest, for tickets_held: a buyer with tickets, the same name in different case with extra spaces, and someone with no tickets.

---

Explain in detail how keeping the sales in a dict keyed by buyer name compares with keeping a list of individual sales, and what each would make easy or hard. Don't change anything.

---

In sold_total, rename the loop variable `name` to `buyer`.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in raffle.py right now, with an example call and its result.

---

Explain in detail how comparing and subtracting datetimes works in Python, and what happens if someone mixes naive and timezone-aware datetimes in the draws. Don't change the code.

---

Add type hints to the functions in raffle.py without changing their behaviour.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
