Let's do TASK.md in two steps.

Step 1: make `parse_line` return a dict with `time` (a datetime), `level` (the word, like "WARN"), `component` (without the brackets, like "billing") and `message` (the rest of the line).

Step 2, for later: the dashboard's format. Our servers log Helsinki time but at a fixed UTC+3 all year (nobody switched DST on), so `time` must become an aware datetime in UTC. `level` becomes the syslog severity number: DEBUG 7, INFO 6, WARN 4, ERROR 3. And lines from the `[health]` component are load balancer noise: `parse_line` returns None for them and `parse` leaves them out.

Do step 1 only for now, then stop. I'll come back for step 2.
