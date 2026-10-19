Let's do TASK.md in two steps.

Step 1: add `parse_scan(line)` to courier.py. The handsets send a line per scan, like "P-1042 DELIVERED 2026-10-16T14:05": the parcel, its status and when it was scanned. Return them as a tuple with the time as a datetime: `parse_scan("P-1042 DELIVERED 2026-10-16T14:05") == ("P-1042", "DELIVERED", datetime(2026, 10, 16, 14, 5))`.

Step 2, for later: `refund`, with the rules support agreed. A delivery is late once it arrives more than 21 minutes after the promised time: the app shows customers a 20-minute window, and drivers get one more minute's grace. A late delivery gets 35% of its fee back: that's about the delivery part of the fee, without the handling. And parcels over 20 kg never get a refund: they go by van, and the van contract doesn't promise a time.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how courier.py works today, function by function, and what could go wrong with the scans it gets: a status in lowercase, a missing time, two DELIVERED scans for one parcel, and so on. Don't change anything.

---

Add a docstring to parse_scan with an example.

---

Change of plan for step 2: finance says percentages are a pain to reconcile, so a late delivery gets a flat £3.18 back, whatever its fee. Still don't start step 2.

---

Explain in detail how datetime.fromisoformat handles the handsets' timestamps, with and without seconds or a UTC offset, and where it could surprise someone. Don't change the code.

---

Add a test file, test_courier.py, using unittest, for parse_scan: a delivered scan, an out-for-delivery scan, extra spaces, and a line that isn't a scan.

---

Explain in detail how scans_for's loop compares with grouping the scans in a dict keyed by parcel, and when the difference would start to matter. Don't change anything.

---

In scans_for, rename the loop variable `item` to `scan`.

---

Explain in detail how a handset whose clock runs a few minutes fast or slow would show up in the scans, and how we could notice it. Don't implement anything.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in courier.py right now, with an example call and its result.

---

Explain in detail what would change if the scans came from a webhook as JSON instead of text lines: the payload, what parse_scan would look like, and the trade-offs. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
