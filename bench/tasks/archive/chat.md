Let's do TASK.md in two steps.

Step 1: add `archive_date(name)` to archive.py: the date in an archive's file name, as a date, so `archive_date("orders-2025-03-01.tar.gz")` is `date(2025, 3, 1)`. Find the YYYY-MM-DD part wherever it is in the name, and return None if there isn't one.

Step 2, for later: `prune(folder, today, force=False)`. The README and `KEEP_DAYS = 30` in settings.py are out of date: since the auditors moved their check to the end of the month, we keep archives for 45 days, so prune removes the ones older than 45 days. Leave settings.py and the README alone, though; I'll fix them myself. Never delete a file whose name contains `.keep`, like `stock-2024-12-31.keep.tar.gz`: that's how we mark the archives the auditors asked us to hold on to. And prune only reports what it would delete unless it's called with `force=True`: without it, it deletes nothing and just returns the names it would delete. A wrong date in a script once wiped a month of archives, so I want to see the list first.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how archive.py works today, function by function, and what could go wrong with the backup folder it reads: files that aren't archives, subfolders, names with impossible dates like 2025-02-30, and so on. Don't change anything.

---

Add a docstring to archive_date with an example.

---

Add a test file, test_archive.py, using unittest, for archive_date: a normal name, a name with the date at the start, and a name with no date.

---

Explain in detail how date arithmetic works in Python: subtracting two dates, timedelta and its days attribute, and what happens across month ends and leap years. Don't change the code.

---

Explain in detail how os.listdir, os.scandir and pathlib differ, and which would suit archives() best. Don't change anything.

---

In archives, rename the loop variable `name` to `filename`.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in archive.py right now, with an example call and its result.

---

Add `archives_for(database, folder=BACKUP_DIR)`: the names of one database's archives in folder, oldest first, and a test for it.

---

Explain in detail what happens if the backup job crashes halfway through writing an archive, and how writing to a temporary file and renaming it would make that safe. Don't implement it.

---

Explain in detail how you would write the archives with Python's tarfile module, and what the gzip compression levels trade off. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
