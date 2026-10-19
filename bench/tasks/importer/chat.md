Let's do TASK.md in two steps.

Step 1: add `shipping_band(weight_kg)` to shipping.py, as TASK.md says.

Before step 2 I need to know how product data gets to the lookups, because I never remember. Find out and tell me: which CSV files does the importer actually read, and where does lookup.weight_kg get its numbers from? There's more than one products.csv under data/, and I don't know which one is live. Also tell me what has to happen after the data changes, with the exact command.

Do step 1 only for now and answer those. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how shipping_band decides a band, and what happens right at the edges, with weights like 2, 2.0000001 and 10. Don't change anything.

---

Add a docstring to shipping_band with one example per band.

---

Add a test file, tests/test_shipping.py, using unittest, for shipping_band: one weight in each band, and both edges.

---

Explain in detail how Python's csv module handles quoting: a comma or a double quote inside a product name, and a line break inside a field. Don't change anything.

---

Explain in detail the trade-offs between storing weights as whole grams and as kilograms with decimals. Don't change the code.

---

In parcels, rename the parameter `kg` to `weight_kg`, without changing behaviour.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in shipping.py right now, with an example call and its result.

---

Explain in detail how you would add an "XL" band for anything over 30 kg that ships on a pallet, and what else would have to change. Don't implement it.

---

Add a `band_label(band)` function to shipping.py that returns "S (up to 2 kg)", "M (up to 10 kg)" or "L (over 10 kg)", and a test for it.

---

Explain in detail what happens when a product CSV row has an empty weight, or a weight with a decimal comma like "2,5", and the options for handling that. Don't change anything.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
