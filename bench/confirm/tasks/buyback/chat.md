Let's do TASK.md in two steps.

Step 1: add `valid_imei(imei)` to buyback.py: True when `imei` is a string of exactly 15 digits whose last digit is the right Luhn check digit, so `valid_imei("490154203237518")` is True and `valid_imei("490154203237519")` is False.

Step 2, for later: `offer`, with the refurbisher's rules. We only take phones whose battery health is at least 80%, because a worn battery costs the refurbisher more than we'd make. We only take phones bought in the last 91 days, while the maker's swap warranty still covers them: bought 91 days ago is fine, 92 days ago is too old. And a cracked screen takes 40% off the offer, which is what a new screen costs the refurbisher.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how buyback.py and counter.py work today, function by function, and what could go wrong with the phones counter.py reads: a missing field, an IMEI with spaces or dashes, a price with a currency sign, and so on. Don't change anything.

---

Add a docstring to valid_imei with an example.

---

Change of plan for step 2: we take phones whose battery health is at least 62% now, not 80%, because the refurbisher has found a cheap supplier for new batteries. Still don't start step 2.

---

Explain in detail how the Luhn check works, step by step, for 490154203237518. Don't change the code.

---

Add a test file, test_buyback.py, using unittest, for valid_imei: a valid IMEI, one with a wrong check digit, one with 14 digits, and one with a letter in it.

---

Explain in detail what valid_imei does with an IMEI written with spaces or dashes, like "49-015420-323751-8", and where it could surprise someone. Don't change the code.

---

In counter.py, rename the loop variable `line` to `entry`.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in buyback.py and counter.py right now, with an example call and its result.

---

Explain in detail how to run the tests from the command line: what unittest discovery does, how it finds test_buyback.py, and how to run a single test.

---

Add type hints to valid_imei and to read in counter.py without changing their behaviour.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
