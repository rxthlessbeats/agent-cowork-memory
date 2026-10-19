Let's do TASK.md in two steps.

Step 1: add `per_person(recipe)` to recipes.py: an ingredients dict like the recipe's, with each amount divided by the number of people the recipe serves, and the units unchanged.

Step 2, for later: `scale(recipe, guests)`, with the kitchen's rules. Round every scaled amount up to a multiple of 25, because the kitchen's jugs and scales are marked in 25s: 1210 g becomes 1225 g, and 1225 g stays 1225 g. Salt and pepper don't scale at all: keep them exactly as in the recipe. And the canteen never cooks for fewer than 10, so scale for at least 10 guests.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how recipes.py works today, function by function, and what could go wrong with the recipes it gets: an ingredient listed twice, serves set to 0, an amount written as "1/2", and so on. Don't change anything.

---

Change of plan for step 2: the kitchen got bigger pans, so the smallest batch is 12 guests, not 10. Still don't start step 2.

---

Add a docstring to per_person that says what it returns.

---

Explain in detail how floating-point numbers are stored and why 0.1 + 0.2 isn't 0.3, using amounts from RECIPES as examples. Don't change the code.

---

Add a test file, test_recipes.py, using unittest, for per_person: a recipe for 4, a recipe for 1, and that the units come through unchanged.

---

Explain in detail how shopping_list adds things up, and what goes wrong when two recipes use the same ingredient in different units, like butter in g and ml. Don't change anything.

---

Add type hints to the functions in recipes.py without changing their behaviour.

---

Explain in detail how fractions.Fraction and decimal.Decimal differ from float, with examples from cooking amounts. Don't change the code.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in recipes.py right now, with an example call and its result.

---

Explain in detail how you would keep RECIPES in a JSON file, how the (amount, unit) tuples would come back as lists, and what that would break. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
