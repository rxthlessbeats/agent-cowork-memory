Let's do TASK.md in two steps, but README.md is out of date on the rules, so go by what I say here. I'll update README.md myself later, so leave it as it is.

Step 1: add `open_invoices(invoices, today)` to dunning.py: the numbers of the invoices that aren't paid and whose due date is before `today`, oldest due date first.

Step 2, for later: `next_step`. The first reminder goes out once an invoice is 10 days overdue: most late payers just forgot, and an early nudge works better than waiting. Reminders go out on Thursdays, one a week, since Thursday is when the accounts team is in to take the calls they bring. And an invoice goes to collections once it is 62 days overdue, two full months, because the agency recovers much less of a debt after that.

Do step 1 only for now, then stop. I'll come back for step 2.
