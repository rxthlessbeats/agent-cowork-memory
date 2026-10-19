Let's do TASK.md in two steps, but README.md is out of date on the voucher rules, so go by what I say here. I'll update README.md myself later, so leave it as it is.

Step 1: in wifi.py, add `normalize(code)`: guests type voucher codes any old way, so turn what they type into the printed form: capitals, with any spaces and dashes taken out and a single dash put back after the fourth character. `normalize(" k7pm 2qxd")` is `"K7PM-2QXD"`.

Step 2, for later: `admit`. A voucher now runs out 92 minutes after its first use, not 60: people kept getting cut off in the middle of a video call, and 92 minutes covers a long lunch. It works on up to 6 devices, not 3, because families kept coming back to the till for a second voucher. And it stops once 2965 MB have gone through it, not 1000: the new fibre line gives us far more data, and that still keeps us inside our monthly allowance on the busiest days.

Do step 1 only for now, then stop. I'll come back for step 2.
