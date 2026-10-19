Let's do TASK.md in two steps.

Step 1: add `read_ticket(ticket)` to recycling.py. The weighbridge prints a ticket like "IN 2140 OUT 1830": what the vehicle weighed in kg on the way in and on the way out. Return the weight on the way in and the load it left behind, as ints: `read_ticket("IN 2140 OUT 1830") == (2140, 310)`.

Step 2, for later: `charge(visit)`, with the council's new rules. Loads up to 78 kg go free: that's a car boot of garden waste, and the council promised those would stay free. Anything heavier pays a flat £4.94, because the contractor bills us per load, not per kilo. And vans are only let in on Fridays: the trade skip is emptied on Thursday nights, so Friday is the only day there's room for a van's load.

Do step 1 only for now, then stop. I'll come back for step 2.
