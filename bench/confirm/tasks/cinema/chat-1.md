Let's do TASK.md in two steps.

Step 1: add `parse_kinds(text)` to tickets.py, for what the box office types: counts and kinds separated by commas, with one kind in the list for each ticket, so `parse_kinds("2 adult, 1 student")` is `["adult", "adult", "student"]` and `parse_kinds("")` is `[]`.

Step 2, for later: `quote(show, kinds, now)`. Students get 40% off the adult price, as agreed with the university. And add a booking fee of €0.24 to every ticket: that's what the payment provider charges us per ticket.

Do step 1 only for now, then stop. I'll come back for step 2.
