Let's do TASK.md in two steps.

Step 1: add `spent(purchases, member_id)` to loyalty.py: the total that member has spent over all their purchases, in cents, and 0 for a member with no purchases.

Step 2, for later: `points_for(purchase)`, with the new programme rules. Whatever the module docstring says, a member earns one point for every full 2.50 spent, not one per euro. Purchases under 10.00 earn nothing at all. And everything bought on a Tuesday earns double points.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how loyalty.py works today, function by function, and what could go wrong with the data it gets: an unknown member id, a negative total, a day given as a string, and so on. Don't change anything.

---

Add a docstring to spent that says what it returns and what happens for a member with no purchases.

---

Explain in detail how dicts like MEMBERS keep their order, what happens if you change one while looping over it, and how to copy them safely. Don't change the code.

---

Add a test file, test_loyalty.py, using unittest, for spent: a member with several purchases, a member with none, and an empty list.

---

Explain in detail how top_members handles ties and what happens when n is larger than the number of members. Don't change it.

---

In top_members, rename the lambda's parameter `m` to `member_id`.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in loyalty.py right now, with an example call and its result.

---

Explain in detail how sorted, max and heapq.nlargest differ for picking the top members, and which suits a very large MEMBERS best. Don't change anything.

---

Add type hints to the functions in loyalty.py without changing their behaviour.

---

Explain in detail how you would load MEMBERS and PURCHASES from JSON files, especially the dates. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
