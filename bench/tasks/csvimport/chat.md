Let's do TASK.md in two steps.

Step 1: uploads are messy. Make `read_rows` strip the spaces around every value and every column name.

Step 2, for later: the rules in `validate`. An email needs an `@` with something on both sides. We only ship to the Nordics, so country must be one of `SE`, `NO`, `DK` or `FI`. Legal says contacts must be 16 or older. Each problem is a string that starts with the column name in square brackets, like `[age] must be 16 or older`.

Do step 1 only for now, then stop. I'll come back for step 2.
