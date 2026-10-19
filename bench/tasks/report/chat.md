Let's build the sales summary from TASK.md, in two steps.

Step 1: add `totals(rows)` to report.py. It takes the rows `load()` returns and gives back a dict from each category to the sum of its amount_cents, as ints.

Step 2, for later: the `summary` command, `python report.py summary [file]`, where file defaults to sales.csv. The amounts are in cents, but print dollars with a dollar sign and two decimals, one category per line, like `food: $21.00`. Biggest total first. Also add a `--top N` option that prints only the first N lines.

Do step 1 only for now, then stop. I'll come back for step 2.
