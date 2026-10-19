Let's do TASK.md in two steps.

Step 1: switch the money to `Decimal`. Unit prices come in as strings like `"19.99"`, and `line_total(qty, unit_price)` returns the exact `Decimal` amount, no rounding. Leave `totals` alone for now.

Step 2, for later: `totals`. The client is in Luxembourg, so VAT is 17%. Their accounting system truncates, so VAT is always rounded down to the cent, never up. Orders whose net is under 50.00 get a 4.95 handling fee added to the net before VAT is worked out; at 50.00 or more there is no fee.

Do step 1 only for now, then stop. I'll come back for step 2.
