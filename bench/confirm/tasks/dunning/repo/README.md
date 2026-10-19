# Dunning

`dunning.next_step(invoice, today)` says what to do about an invoice on a given day: nothing (`None`), send a `"reminder"`, or hand it to `"collections"`.

## Rules

An unpaid invoice gets its first reminder once it is 14 days overdue. Reminders go out on Mondays, one a week, until the invoice is paid. Once an invoice is 90 days overdue it goes to the collections agency instead. Invoices too small to be worth chasing are left alone.

Run it every morning with `python3 daily.py invoices.json`.
