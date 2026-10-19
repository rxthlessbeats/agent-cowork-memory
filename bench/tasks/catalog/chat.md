Let's do TASK.md in two steps.

Step 1: add `words(text)` to catalog.py: the lowercase words in text, where anything that isn't a letter or a digit separates words, so `words("Desk-Lamp, 2 pack")` is `["desk", "lamp", "2", "pack"]`.

Step 2, for later: `search(products, query)`, with the shop's rules. Whatever the module docstring says, match the query against product names only, never tags: the tags are full of marketing noise. Hide anything with fewer than 3 units in stock, since those are usually promised to orders already. And show the products with the most units in stock first.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how catalog.py works today, function by function, and what could go wrong with the products it gets: duplicate SKUs, a missing key, a SKU in lowercase, and so on. Don't change anything.

---

Add a docstring to words with an example.

---

Change of plan for step 2: marketing wants the expensive products seen first, so sort the matches by price, most expensive first, not by how many are in stock. Still don't start step 2.

---

Explain in detail how words handles punctuation, digits, underscores and accented letters like the é in "Café", and where it could surprise someone. Don't change the code.

---

Add a test file, test_catalog.py, using unittest, for words: a plain name, a name with hyphens and commas, mixed case, and an empty string.

---

Explain in detail how by_sku's loop compares with looking products up in a dict keyed by SKU, and when the difference would start to matter. Don't change anything.

---

In by_sku, rename the loop variable `product` to `item`.

---

Explain in detail how str.lower, str.casefold and unicodedata.normalize differ, with examples where they give different results. Don't change the code.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in catalog.py right now, with an example call and its result.

---

Explain in detail what would change if PRODUCTS lived in a SQLite table instead of a Python list: the schema, what by_sku would look like as a query, and the trade-offs. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
