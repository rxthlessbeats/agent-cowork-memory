Let's do TASK.md in two steps.

Step 1: add `parse_amount(text)` to taxbands.py. The payroll export writes incomes like "12,345.67", with commas between the thousands and sometimes spaces around them; return the amount as a Decimal, so `parse_amount(" 12,345.67 ")` is `Decimal("12345.67")`. Use it in export.py's `read` instead of `Decimal(income)`.

Step 2, for later: `tax`, with the bands our accountant gave us. The first 4145 of a year's income is tax-free, and only the part above 4145 is taxed, because that's this year's allowance for our kind of contract. Anyone under 18 pays no tax at all, since the export includes the apprentices and the training scheme covers their tax. And anyone aged 65 or over pays half the tax they would otherwise pay, because the pensioners' relief covers the other half.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how taxbands.py and export.py work today, function by function, and what could go wrong with the lines export.py reads: a missing tab, an age that isn't a number, an empty line, and so on. Don't change anything.

---

Add a docstring to parse_amount with an example.

---

Explain in detail why Decimal is a better fit than float for these amounts, with examples where float gives a surprising result. Don't change the code.

---

Add a test file, test_taxbands.py, using unittest, for parse_amount: a plain amount, one with commas between the thousands, one with spaces around it, and a whole number.

---

Explain in detail what parse_amount does with inputs like "1,2,3", "12.345,67", "-500" and "1e3", and where it could surprise someone. Don't change the code.

---

In export.py, rename the loop variable `row` to `line`.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in taxbands.py and export.py right now, with an example call and its result.

---

Explain in detail how to run the tests from the command line: what unittest discovery does, how it finds test_taxbands.py, and how to run a single test.

---

Add type hints to parse_amount and to read in export.py without changing their behaviour.

---

Explain in detail what would change if export.py read the file with the csv module instead of splitting lines by hand. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
