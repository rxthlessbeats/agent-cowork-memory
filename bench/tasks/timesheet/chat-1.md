Let's do TASK.md in two steps.

Step 1: make `shift_hours` handle night shifts: when the end time is earlier than the start, the shift runs past midnight, so `shift_hours("22:00", "06:00")` is 8.0. Nothing else changes yet.

Step 2, for later: what our agreement with staff says. Overtime is every hour past 7.5 in one day, and overtime hours pay 1.4 times the rate. Sunday shifts pay double for every hour, overtime or not.

Do step 1 only for now, then stop. I'll come back for step 2.
