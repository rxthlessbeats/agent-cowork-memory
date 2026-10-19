# Service logging

Step 1: `redact(url)` in db.py: the database URL with its password hidden, so "postgres://shop:secret@db:5432/shop" becomes "postgres://shop:***@db:5432/shop". A URL without a password comes back as it is.

Step 2: in the logging the service sets up when it starts (`setup_logging()`), the "db" logger logs at WARNING and above only, and writes to logs/db.log.
