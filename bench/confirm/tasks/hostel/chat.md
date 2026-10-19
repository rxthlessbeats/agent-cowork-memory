Let's do TASK.md in two steps.

Step 1: add `stay_dates(arrival, nights)` to hostel.py: the date of each night of the stay, in order, so `stay_dates(date(2026, 10, 16), 3)` is the 16th, 17th and 18th of October.

Step 2, for later: `bed_price` and `city_tax`. The city tax is 4.38 per guest per night; that's this year's rate from the city. Sunday nights, the night from Sunday to Monday, are 17% off the bed price, because that's our emptiest night. And stays of 58 nights or more pay no city tax at all, because the city counts those guests as residents.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how stay_dates works and what it returns for a stay of zero nights, a negative number of nights, and a stay over New Year's Eve. Don't change anything.

---

Add a docstring to stay_dates with an example.

---

Change of plan for step 2: I checked the city's rules again, and guests count as residents from 45 nights, not 58. So stays of 45 nights or more pay no city tax. Still don't start step 2.

---

Explain in detail how date arithmetic with timedelta handles month ends and leap years, with examples. Don't change the code.

---

Add a test file, test_hostel.py, using unittest, for stay_dates: a one-night stay, a stay across a month end, and a zero-night stay.

---

Make stay_dates raise ValueError for a negative number of nights.

---

Explain in detail what DORMS in hostel.py describes and how you'd find which dorms still have a free bed on a given night. Don't change anything.

---

Explain in detail how stay_dates would behave if someone passed a datetime instead of a date as the arrival, and whether that could cause trouble. Don't change the code.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in hostel.py right now, with an example call and its result.

---

Explain in detail how you'd store bookings in SQLite instead of in memory: the tables, the query for free beds on a night, and the trade-offs. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
