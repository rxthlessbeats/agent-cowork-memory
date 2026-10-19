Let's do TASK.md, with two changes from DESIGN.md: store the entries in SQLite with the sqlite3 module instead of a JSON file, and make entries expire after 10 minutes, not an hour. I'll update DESIGN.md myself later, so leave it as it is.

Step 1: write `class Cache` with `__init__(self, path, now=time.time)` that opens the SQLite database at path and creates its table. `now` lets tests control the time.

Step 2, for later: `set(key, value)` and `get(key)`. `get` returns None when a key is missing or expired, and deletes an expired entry when it finds one.

Do step 1 only for now, then stop. I'll come back for step 2.
