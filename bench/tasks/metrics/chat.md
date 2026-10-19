Let's do TASK.md in two steps.

Step 1: add `escape(value)` to exporter/textfmt.py, as TASK.md says.

Before step 2 I need to know where the labels on the metrics come from, because I never remember. There's labels.example.ini at the top of the repo and I'm not sure the exporter reads it. Find out and tell me: which file do the labels come from, and which code reads it? And is labels.example.ini used at all?

Do step 1 and answer those, but don't start step 2: I'll come back for it later. Meanwhile I have some other small things.

---

Explain in detail how the Prometheus text format works: the # HELP and # TYPE lines, how labels and values are written, and what a scraper does with a line it can't parse. Don't change anything.

---

Give escape and line docstrings with an example call and its result each.

---

Add a test file, tests/test_textfmt.py, using unittest, for escape and line: a plain value, a quote, a backslash, a newline, and a line with two labels.

---

Explain in detail why label values need escaping but label names don't, and which characters metric and label names may contain. Don't change the code.

---

Explain in detail how Prometheus computes rate() over a counter like shop_orders_total, and what happens when the exporter restarts and the counter goes back to 0. Don't change anything.

---

In textfmt.line, rename the local variable `pairs` to `rendered`, without changing behaviour.

---

Write a NOTES.md with a "textfmt" section describing each public function in exporter/textfmt.py right now, with an example call and its result.

---

Add `valid_name(name)` to exporter/textfmt.py: True if name is a valid Prometheus metric name (`[a-zA-Z_:][a-zA-Z0-9_:]*`), and a test for it.

---

Explain in detail the difference between a counter, a gauge and a histogram, with an example of each from a web shop. Don't change anything.

---

Explain in detail how Python writes floats like 0.1 + 0.2, 1e21, NaN and infinity with str and repr, and how the Prometheus text format expects them. Don't change the code.

---

Explain in detail the trade-offs of pushing metrics to a Pushgateway instead of letting Prometheus scrape them. Don't change anything.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
