Let's do TASK.md in two steps.

Step 1: add `call_name(n)` to bingo.py: how the caller says a number, which is its column's letter, a hyphen and the number, with B for 1 to 15, I for 16 to 30, N for 31 to 45, G for 46 to 60 and O for 61 to 75. So `call_name(7)` is `"B-7"` and `call_name(75)` is `"O-75"`.

Step 2, for later: `payout(game)`, with the hall's rules. The full-house prize is 44% of the card sales; the rest pays for the hall and the charity. A full house in 34 calls or fewer wins the jackpot as well. And there's no jackpot on Tuesdays, whatever the calls: Tuesday is charity night, and that money goes to the charity instead.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how bingo.py and hall.py work today, and what draw does with its seed. Don't change anything.

---

Add a docstring to call_name with an example.

---

Change of plan for step 2: the owner wants the jackpot won less often, so it takes a full house in 32 calls or fewer, not 34. Still don't start step 2.

---

Explain in detail what call_name does with 0, 76, -3, 15.0 and "7", and where it could surprise someone. Don't change the code.

---

Add a test file, test_bingo.py, using unittest, for call_name: the first and the last number of each column.

---

Explain in detail how random.Random(seed).shuffle works, why the same seed always gives the same order, and whether that's safe for a game with money on it. Don't change anything.

---

In draw, rename the variable `numbers` to `balls`.

---

Explain in detail how 90-ball bingo differs from our 75-ball game, and what call_name would need for it. Don't implement it.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in bingo.py right now, with an example call and its result.

---

Explain in detail how the secrets module compares with random for drawing numbers, with examples. Don't change the code.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
