Let's do TASK.md in two steps.

Step 1: add `made_on(name)` to retention.py: the date in a backup's file name, so `made_on("backup-2026-03-02.tar.gz") == date(2026, 3, 2)`. Leave `keep` alone for now.

Step 2, for later: the rules in `keep`. Dailies stay for 10 days, not 7: today's backup and the 9 before it. And the weekly backup we keep is Wednesday's, not Sunday's; it's the first one after ops patch the servers.

Do step 1 only for now, then stop. I'll come back for step 2.
