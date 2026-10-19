Let's do TASK.md in two steps.

Step 1: add `redact(url)` to db.py, as TASK.md says.

Before step 2 I need to know how the service's logging gets configured, because I never remember. Find out and tell me: which ini file does setup_logging load when the service starts, and what decides that? There's more than one ini file in logconf/, and I don't know which one is live.

Do step 1 and answer those. Don't start step 2; I'll come back for it later. Meanwhile I have some other small things.

---

Explain in detail how redact handles a URL without a password, one with a port, one whose password contains an @, and one without a scheme. Don't change anything.

---

Add a docstring to redact with an example.

---

Add a test file, tests/test_db.py, using unittest, for redact: a URL with a password, one without, and one with a port.

---

Explain in detail what urllib.parse.urlsplit returns for a database URL like postgres://shop:secret@db:5432/shop, attribute by attribute, and where it surprises people. Don't change anything.

---

In db.py, rename connect's parameter `url` to `dsn`, without changing behaviour.

---

Write a NOTES.md with a "db.py" section describing each public function in db.py right now, with an example call and its result.

---

Explain in detail the differences between keeping secrets in environment variables, a .env file and a secrets manager, and the risks of each. Don't change anything.

---

Add `with_database(url, name)` to db.py, returning the URL with its database name replaced, so with_database("postgres://shop@db:5432/shop", "shop_test") gives "postgres://shop@db:5432/shop_test", and a test for it.

---

Explain in detail how you'd retry a failed database connection: backoff, jitter, and which errors deserve a retry. Don't implement it.

---

Explain in detail how connection pooling works for a service like this and which settings matter: pool size, timeouts, recycling. Don't implement it.

---

Explain in detail how you'd add a health check that tells whether the database is reachable, and what it should return. Don't implement it.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
