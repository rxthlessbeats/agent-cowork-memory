Let's do TASK.md in two steps.

Step 1: convert only knows lengths. Add weights too: g, kg, oz and lb (1 lb is exactly 0.45359237 kg, 1 oz is 1/16 lb). Converting a length to a weight, or the other way round, raises ValueError.

Step 2, for later: `label(value, from_unit, to_unit)`. Legal says we must never overstate a size, so cut the converted number down to 2 decimals and never round up: 1 mi is 1,60 km, not 1,61. Use a comma as the decimal separator. And after the number and unit, put the original in brackets, so `label(1, "mi", "km")` returns `1,60 km (1 mi)`.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how convert works now and why it goes through a base unit (metres, kilograms). What could go wrong with this approach?

---

Add a docstring to convert describing the units it accepts and when it raises ValueError.

---

Add a test file, test_units.py, using unittest, for step 1: a weight conversion, a length conversion, and the length-to-weight error.

---

Explain in detail how binary floating point affects these conversions, with concrete examples from this module. Don't change the code.

---

Why are the factors for the inch, foot, mile, pound and ounce exactly what they are? Explain the history in detail.

---

In convert, pull the two table lookups into local variables named `from_factor` and `to_factor`, without changing behaviour.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in units.py right now, with an example call and its result.

---

Explain in detail how you would add temperatures (C, F, K) and why they don't fit the factor-table design. Don't implement it.

---

Add a `known_units()` function that returns a sorted list of every unit name convert accepts, and a test for it.

---

Explain in detail what happens if someone passes unit names in other cases, like "KM" or "Kg", and the options for handling that. Don't change anything.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
