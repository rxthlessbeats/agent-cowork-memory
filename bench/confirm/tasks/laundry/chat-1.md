Let's do TASK.md in two steps.

Step 1: add `slot_start(when)` to laundry.py: the start of the slot that `when` falls in, or None when it falls outside every slot. So 10:15 is in the 9:00 slot, and 21:30 is in none.

Step 2, for later: `can_book`, with the house rules the residents voted for. No slot on a Friday can be booked at all: Friday is the day the caretaker cleans and services the machine. And a slot can be booked at most 66 hours before it starts, so nobody can grab the whole weekend days ahead: bookings for the Monday 7:00 slot open on Friday at 13:00.

Do step 1 only for now, then stop. I'll come back for step 2.
