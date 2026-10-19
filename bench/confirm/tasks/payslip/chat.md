Let's do TASK.md in two steps.

Step 1: add `parse_shift(line)` to payslip.py: a line from the till's clock-in export, like `2026-03-05 7.5`, becomes a shift, `{"day": date(2026, 3, 5), "hours": Decimal("7.5")}`. Extra spaces around either part are fine.

Step 2, for later: `payslip`, done the way we actually run payroll. A month's payslip covers the shifts from the 23rd of the month before up to and including the 22nd: the accountant needs the last week of the month to check the timesheets. Nobody pays into the pension in a month when they earn less than 1561.00 gross, the scheme's lower limit; from 1561.00 up, they pay it on the whole gross. And payday is the last Thursday of the month, since the bank only sends our payments out on Thursdays.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how payslip.py works today, function by function, and what could go wrong with the data it gets: a rate given as a float, negative hours, a shift with no hours key, and so on. Don't change anything.

---

Add a docstring to parse_shift with an example.

---

Explain in detail how Decimal's quantize and its rounding modes work, and why cents uses ROUND_HALF_UP instead of the default. Don't change the code.

---

Add a test file, test_payslip.py, using unittest, for parse_shift: a plain line, a line with extra spaces, hours without a decimal point, and a line with a date that doesn't exist.

---

Explain in detail what parse_shift does with lines like `2026-03-05 7,5`, `05/03/2026 7.5` or an empty line, and where it could surprise someone. Don't change the code.

---

In total_hours, rename the loop variable `shift` to `entry`.

---

Explain in detail how float and Decimal differ for money, with examples where adding up wages in floats goes wrong. Don't change anything.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in payslip.py right now, with an example call and its result.

---

Add type hints to the functions in payslip.py without changing their behaviour.

---

Explain in detail how you would read the clock-in export from a CSV file with the csv module, with a header row and blank lines in it. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
