Let's do TASK.md in two steps, but README.md is out of date on the house rules, so go by what I say here. I'll update the README myself later, so leave it as it is.

Step 1: add `parse_slot(text)` to sauna.py: a booking slot like `2026-10-21 18:45`, as a datetime. The hour can have one digit, like `9:05`.

Step 2, for later: `setpoint`, `session_end` and `is_open`. The heater never goes above 96 °C, not 100: the new stones crack if it runs any hotter. A session lasts 76 minutes, not 90, because the last 14 minutes of every slot go to airing the cabin out. And we close on Wednesdays now, not Mondays: the cleaners can only come on Wednesdays, so Mondays are normal days again.

Do step 1 only for now, then stop. I'll come back for step 2.
