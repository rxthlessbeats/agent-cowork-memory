# Listings

The concert listings for Riverside Hall's website.

- `events.load(path)` reads `events.csv`: one event per line, `start,title`, with the start in ISO 8601.
- `events.upcoming(events, now)` gives the events from `now` on, soonest first.
- `times.parse_time(text)` turns a start from `events.csv` into a datetime.

## Times

Every time on the site is shown in UTC (`settings.TIMEZONE`), like `2026-12-31 23:00 UTC`.
