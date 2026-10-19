Let's do TASK.md in two steps.

Step 1: add `parse(number)` to receipts.py. It splits a receipt number into its year and counter, as ints: `parse("2026-0042") == (2026, 42)`. Leave `next_number` alone for now.

Step 2, for later: `next_number`. Our financial year starts on 1 April, so that's when the counter goes back to 1, and the year in the number is the year the financial year began: a receipt from 31 March 2027 still says 2026. And the counter has 5 digits, not 4: 2026-00042.

Do step 1 only for now, then stop. I'll come back for step 2.
