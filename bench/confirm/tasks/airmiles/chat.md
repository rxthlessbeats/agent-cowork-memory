Let's do TASK.md in two steps, but the README's earning rules are out of date, so go by what I say here. I'll update README.md myself later, so leave it as it is.

Step 1: add `parse_flight(line)` to miles.py: a line from the bookings export, with the date, the distance and the cabin separated by spaces, as a flight dict, so `parse_flight("2026-11-08 3451 business")` is `{"date": date(2026, 11, 8), "distance": 3451, "cabin": "business"}`.

Step 2, for later: `earn(flight)`, with this year's rules. Every flight earns at least 911 miles now, not 500: that's what our partner airline gives, so members earn the same with either of us. Business class earns 18% more than economy, not 50%: finance cut the bonus when business fares came down. And the double-miles day is Sunday, not Saturday, since Sunday flights are the emptiest now.

Do step 1 only for now, then stop. I'll come back for step 2.
