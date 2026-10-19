Let's do TASK.md in two steps.

Step 1: add `parse_booking(text)` to rooms.py: it turns a line like "Fjord 2026-03-03 10:00 45" into a booking dict, with the start as a datetime and the minutes as an int, and raises ValueError for a room that isn't in ROOMS.

Step 2, for later: `can_book(booking, now)`, with the house rules. A booking can last at most 73 minutes: the rooms are for short meetings, and longer ones go in the event hall. Nothing can be booked more than 56 days ahead, because the landlord's calendar only syncs eight weeks. And no bookings on Fridays, when the cleaners do the rooms.

Do step 1 only for now, then stop. I'll come back for step 2.
