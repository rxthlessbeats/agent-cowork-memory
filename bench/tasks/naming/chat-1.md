Let's do TASK.md in two steps.

Step 1: make `export_name` raise `ValueError` for a report that isn't in `REPORTS`, so a typo like `"sale"` fails loudly. Nothing else changes yet.

Step 2, for later: the archive team's convention. Join the parts with dots, report first, then client, then date: `sales.ACMECORP.02032026.csv`. The client part is the client's name in capitals with everything but letters and digits dropped, so `Acme Corp.` becomes `ACMECORP`. Dates are DDMMYYYY.

Do step 1 only for now, then stop. I'll come back for step 2.
