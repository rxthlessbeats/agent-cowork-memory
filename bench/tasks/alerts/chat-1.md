Let's do TASK.md in two steps.

Step 1: make `parse` return the percent as a float, with or without a trailing `%`, so `parse("web-1 /var 91.5%")` is `("web-1", "/var", 91.5)`. Nothing else changes yet.

Step 2, for later: what ops agreed on. A disk is a warning from 83 percent used and critical from 96. Go by the lowest of the last three readings, so a single spike never alerts. The message is the level in capitals, then host:mount, then the latest reading rounded to a whole percent: `WARNING web-1:/var 85%`.

Do step 1 only for now, then stop. I'll come back for step 2.
