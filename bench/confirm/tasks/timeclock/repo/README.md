# Time clock

`timeclock.py` turns the shifts from the clock-in terminal into pay. A shift is a dict with "start" and "end", datetimes on the same day.

## Pay rules

- Every hour is paid at the base rate.
- Hours past 8 in one shift are overtime, paid at time and a half.
- Sunday shifts pay double.
- Shifts longer than 6 hours get a 5.00 meal allowance.
