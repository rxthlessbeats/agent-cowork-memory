Let's do TASK.md in two steps.

Step 1: add `parse(line)` to auction.py for the bid log lines: `parse("2026-05-07 19:42:05 paddle-17 5200")` is `(datetime(2026, 5, 7, 19, 42, 5), "paddle-17", 5200)`.

Step 2, for later: `winner`. A bid only counts if it's at least 3.72 more than the highest bid that counts so far, so that every raise covers the card fee on it. No bid under 48.00 counts, because handling a lot costs the porters that much. And a bid counts only up to two hours after the lot opens; anything later is too late.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how auction.py works today, function by function, and what could go wrong with the bid lines it gets: a missing amount, an amount with a decimal point, a paddle name with a space in it, and so on. Don't change anything.

---

Add a docstring to parse with an example.

---

Change of plan for step 2: a bid counts only up to 109 minutes after the lot opens, not two hours. The sale has more lots now and has to be over before the hall closes. Still don't start step 2.

---

Explain in detail how parse handles the seconds in a time, leading zeros in an amount like 0005200, and where it could surprise someone. Don't change the code.

---

Add a test file, test_auction.py, using unittest, for parse: an ordinary line, a line with a big amount, and a line with spaces at the end.

---

Explain in detail how sorting the bid lines as strings compares with sorting them by their parsed time, and when the two would differ. Don't change anything.

---

Make parse return a namedtuple, Bid(when, bidder, cents), instead of a plain tuple, so the fields have names.

---

Explain in detail how float, Decimal and int differ for amounts of money, with examples where floats go wrong. Don't change the code.

---

Write a NOTES.md with a "Functions" section describing each function in auction.py that works today, with an example call and its result. Leave out anything that isn't built yet.

---

Explain in detail what would change if the bids came from a SQLite table instead of a log file: the schema, what parse would become, and the trade-offs. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
