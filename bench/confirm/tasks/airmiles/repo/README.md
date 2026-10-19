# Air miles

Members of the loyalty programme earn miles on every flight they take with us. `miles.earn(flight)` works out what a flight earns. A flight is a dict with `date`, `distance` (miles flown) and `cabin` ("economy" or "business").

## Earning

A flight earns one mile for each mile flown. Every flight earns at least 500 miles. Business class earns 50% more than economy. Flights on a Saturday earn double miles.

No flight earns more than the cap in settings.py.
