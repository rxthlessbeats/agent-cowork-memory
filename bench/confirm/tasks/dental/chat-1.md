Let's do TASK.md in two steps.

Step 1: add `hours_notice(appointment, cancelled_at)` to dental.py: how many hours before the appointment's start the cancellation came, as a float. Cancelling at 15:30 for 09:00 two days later gives 41.5.

Step 2, for later: `cancellation_fee`. Cancelling with less than 72 hours' notice is charged, because we need three days to fill a chair from the waiting list. The charge is 5.37: it's only there to make people call in time, not to make money. And appointments on a Friday are never charged, since Friday is our emergency day and those chairs fill within the hour.

Do step 1 only for now, then stop. I'll come back for step 2.
