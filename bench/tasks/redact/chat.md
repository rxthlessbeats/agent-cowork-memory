Let's do TASK.md in two steps.

Step 1: in format_event, replace the value of any `password` or `token` key with `[REDACTED]`, matching key names in any case.

Step 2, for later: hide `api_key` the same way, and look inside nested dicts and lists too. For `card_number`, keep the last 4 digits and replace every other digit with `*`, like `************4242`. Never change the event that was passed in; work on a copy.

Do step 1 only for now, then stop. I'll come back for step 2.
