Let's do TASK.md in two steps.

Step 1: add `parse_reading(line)` to plants.py. The sensors send lines like "tomatoes 2026-10-16T06:30 41.5%": the bed, when the reading was taken, and the soil moisture in percent, sometimes without the % sign. Return them as a tuple of the bed, a datetime and a float: `parse_reading("tomatoes 2026-10-16T06:30 41.5%") == ("tomatoes", datetime(2026, 10, 16, 6, 30), 41.5)`.

Step 2, for later: `watering`, with the head grower's rules. A bed only gets water when its moisture is under 39%: the tomatoes split if we water them while the soil is still damp. When a bed does get water, the drip runs for 46 minutes, because that's how long it takes to soak down to the roots in these beds. And no watering at all on Thursdays: that's feed day, and the liquid feed wets the soil anyway.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how plants.py works today, function by function, and what could go wrong with the lines the sensors send: a missing % sign, a comma as the decimal mark, extra spaces, a bed name we don't know, and so on. Don't change anything.

---

Add a docstring to parse_reading with an example.

---

Explain in detail how datetime.fromisoformat handles timestamps like the sensors', with and without seconds or a UTC offset, and where it could surprise someone. Don't change the code.

---

Add a test file, test_plants.py, using unittest, for parse_reading: a reading with a % sign, one without, one with extra spaces, and a line that isn't a reading.

---

Explain in detail how latest's loop compares with sorting the readings or using max with a key, and when the difference would start to matter. Don't change anything.

---

In latest, rename the variable `best` to `newest`.

---

Explain in detail how float("41.5"), float("41,5"), float(" 41.5 ") and float("nan") behave, and which of those a sensor line could plausibly contain. Don't change the code.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in plants.py right now, with an example call and its result.

---

Explain in detail what would change if the sensors sent JSON over MQTT instead of text lines: the message format, what parse_reading would look like, and the trade-offs. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Explain in detail how a sensor whose clock runs a few minutes fast or slow would affect which reading latest picks, and how we could notice it. Don't implement anything.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
