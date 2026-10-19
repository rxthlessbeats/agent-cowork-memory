Let's do TASK.md in two steps.

Step 1: add `invalid(response)` to survey.py: the ids of the questions whose answer is neither None nor a whole number from 1 to 5, in question order. A question missing from the response counts as skipped, not invalid.

Step 2, for later: `score(response)`, the way HR wants it. Questions q3 and q6 are worded the other way round, so flip them before averaging: 1 counts as 5, 2 as 4, and so on. Whatever the module docstring says, q1 counts double. And a response with fewer than 6 answers gets no score at all: return None.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how survey.py works today, function by function, and what could go wrong with the responses it gets: extra keys, answers given as strings, a question id in capitals, and so on. Don't change anything.

---

Change of plan for step 2: HR says the board only follows q8, so q8 is the question that counts double, not q1. Still don't start step 2.

---

Add a docstring to invalid that says what counts as invalid and what doesn't.

---

Explain in detail how Python decides what a whole number is here: int, bool, float.is_integer and numbers.Integral, and which of them invalid should care about. Don't change the code.

---

Add a test file, test_survey.py, using unittest, for invalid: a clean response, answers out of range, an answer given as a string, and a skipped question.

---

Explain in detail what QUESTIONS being a list rather than a tuple or a set means for the functions here, and when each would be the better choice. Don't change anything.

---

Add type hints to the functions in survey.py without changing their behaviour.

---

Explain in detail how you would load responses from the survey tool's CSV export, with blank cells and stray spaces, into this dict format. Don't implement it.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in survey.py right now, with an example call and its result.

---

Explain in detail how you would keep responses anonymous if they were stored, and what could still identify someone in a small team. Don't change anything.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
