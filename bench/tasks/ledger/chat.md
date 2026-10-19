Let's do TASK.md in two steps, but ledger.py's docstring is wrong about how amounts are shown, so go by what I say here. I'll fix the docstring myself later, so leave it as it is.

Step 1: in ledger.py, add `parse_amount(text)`: the amount in a string like `"19.99"` or `"-3.5"`, as an exact `Decimal`, no rounding.

Step 2, for later: `fmt(amount)`, which takes a `Decimal` and returns the text the report shows. Round to whole cents with banker's rounding, half to even, so 2.345 becomes 2.34 and 2.355 becomes 2.36: our accountant reconciles against the bank, and the bank rounds that way. Negative amounts go in parentheses, with no minus sign: -12.5 is `(12.50)`. And separate thousands with commas: `1,234.50`.

Do step 1 only for now, then stop. I'll come back for step 2.
