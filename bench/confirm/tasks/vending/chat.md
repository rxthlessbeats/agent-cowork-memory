Let's do TASK.md in two steps.

Step 1: add `fill_percent(slot)` to vending.py: how full a slot is, as a whole percent of its capacity, rounded down, so a slot with 3 items left out of 8 is 37.

Step 2, for later: `alerts`, with the thresholds the operators asked for. A slot is low when it's below 26% full, and the machine gets `low_stock` when any of its slots is low: below that, a slot usually sells out before the driver's next round. The coin box is full from 810 coins on: it holds about 900, but it starts jamming well before that. And a machine is `offline` once it last reported in more than 48 minutes ago: the modems in the basement drop out for a while every so often, and we don't want an alarm each time.

Do step 1 only for now, then stop. I'll come back for step 2.
