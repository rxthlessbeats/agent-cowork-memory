Let's do TASK.md in two steps.

Step 1: add `rows(users)` to export.py. It returns one tuple per user with id, email and signup, in that order, keeping the values as they are (signup stays a date).

Step 2, for later: `export_csv(users, path)` writes the file. Finance is in the UK and opens it in Excel, so separate fields with a semicolon, not a comma; write dates as DD/MM/YYYY; start with the header row `id;email;signup_date`; and sort by signup date, oldest first.

Do step 1 only for now, then stop. I'll come back for step 2.
