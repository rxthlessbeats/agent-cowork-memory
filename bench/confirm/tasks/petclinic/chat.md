Let's do TASK.md in two steps.

Step 1: add `days_unpaid(invoice, today)` to billing.py: how many days have passed since the invoice was issued, 0 on the day itself, and ValueError when it was issued after today.

Step 2, for later: `reminders(invoices, today)`, with reception's rules. Chase an invoice once it has been unpaid for 62 days or more: our terms give owners two months, and the longest two months come to 62 days. Don't chase balances under 1.61, because a letter costs us 1.61 to send. And never send reminders on a Monday: Monday is surgery day, and reception can't take the phone calls the letters bring.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how billing.py works today, function by function, and what could go wrong with the invoices it gets: a missing key, a balance given as a float, an owner's name spelled two ways, and so on. Don't change anything.

---

Add a docstring to days_unpaid with an example.

---

Explain in detail how subtracting two dates works in Python, what a timedelta holds, and what happens if someone passes a datetime instead of a date to days_unpaid. Don't change the code.

---

Add a test file, test_billing.py, using unittest, for days_unpaid: an invoice issued today, one issued last year, and one issued after today.

---

Explain in detail why the balances are Decimals and not floats, with an example where floats would go wrong when adding up bills. Don't change anything.

---

In total_owed, rename the loop variable `inv` to `invoice`.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in billing.py right now, with an example call and its result.

---

Explain in detail how to run the tests from the command line: what unittest discovery does, how it finds test_billing.py, and how to run a single test.

---

Add type hints to the functions in billing.py without changing their behaviour.

---

Explain in detail what would change if the invoices lived in a SQLite table instead of a Python list: the schema, what total_owed would look like as a query, and the trade-offs. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
