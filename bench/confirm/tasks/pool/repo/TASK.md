# Pool bookings

The front desk books swimmers into sessions by hand and wants the till to do it. Add `book(session, people)` to pool.py. A session is a dict with `start` ("YYYY-MM-DD HH:MM") and `booked` (how many swimmers are booked already); each person is a dict with `age` and `member` (True or False). It returns what the group pays, in cents, or None when the booking can't be taken. Children pay the child price, and members pay less.
