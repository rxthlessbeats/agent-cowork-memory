Let's do TASK.md in two steps, but the README is out of date on scoring, so go by what I say here. I'll update the README myself later, so leave it as it is.

Step 1: make `mark` in quiz.py forgiving about how teams write their answers: ignore case and spaces around an answer, so " paris " is correct when the right answer is "Paris". A blank answer, empty or just spaces, counts as skipped, like None. Nothing else changes yet.

Step 2, for later: `score(answers)` with the quizmaster's new rules, so teams stop guessing wildly: 10 points for each correct answer, minus 5 for each wrong one, and 0 for a skipped one.

Do step 1 only for now, then stop. I'll come back for step 2.
