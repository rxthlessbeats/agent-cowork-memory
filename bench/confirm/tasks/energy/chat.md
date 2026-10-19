Let's do TASK.md in two steps, but the README is out of date on the idle fee and the member discount, so go by what I say here. I'll update the README myself later, so leave it as it is.

Step 1: add `idle_minutes(full, unplugged)` to charging.py: the whole minutes a car stayed plugged in after it was full, so from 10:00:00 to 11:15:40 is 75.

Step 2, for later: `session_cost`. A car may stay plugged in for up to 58 minutes after it's full without an idle fee, since most drivers are in the café, and the lunch rush was getting fined. Past that, the idle fee is a flat 9.35: the old fee was cheaper than the car park, so people left their cars on the chargers. And members get 14% off the energy, which is what the new membership price was set for.

Do step 1 only for now, then stop. I'll come back for step 2.
