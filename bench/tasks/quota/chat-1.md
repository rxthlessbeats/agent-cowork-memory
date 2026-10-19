Let's do TASK.md in two steps.

Step 1: add `percent(used, limit)` to quota.py: how much of the quota is used, as a percentage, so `percent(GB, 4 * GB) == 25.0`. A limit of 0 means the user has no quota; return 0.0 for it. Leave `warning` alone for now.

Step 2, for later: the warning itself. Warn from 88% used, not 80%. And the message shows the percentage as a whole number, always rounded up: 90.2% shows as 91%.

Do step 1 only for now, then stop. I'll come back for step 2.
