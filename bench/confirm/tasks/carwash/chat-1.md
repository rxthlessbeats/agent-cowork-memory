Let's do TASK.md in two steps.

Step 1: add `parse_log(line)` to carwash.py, which `sessions` already calls. The bay controller logs one line per session, like "B2 C-1042 14:05:10 14:12:41": the bay, the customer's card, and when the jet went on and off. Return the bay, the card and how many seconds the jet ran: `parse_log("B2 C-1042 14:05:10 14:12:41") == ("B2", "C-1042", 451)`.

Step 2, for later: `charge(session)`. The jet is 15p a minute, to match the garage on the ring road, and every started minute counts, so 61 seconds is two minutes: the card terminal can only bill whole minutes. And nobody pays for more than 22 minutes: past that the jet keeps running for free, because people were racing the clock and driving off with the car half rinsed.

Do step 1 only for now, then stop. I'll come back for step 2.
