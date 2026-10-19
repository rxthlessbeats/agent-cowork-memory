Let's do TASK.md in two steps, but the docstring in validators.py is left over from the old site, so go by what I say here. I'll update the docstring myself later, so leave it as it is.

Step 1: `valid_email` lets through addresses with spaces in them or a second @. Make it refuse both, so `ana smith@example.com` and `ana@@example.com` are invalid, while `ana@example.com` still passes.

Step 2, for later: `valid_username(name, taken)`, with the new site's rules. A username is 4 to 16 characters: squatters grabbed every 3-letter name, and 16 is what fits on the profile badge. Letters, digits and underscores only. And it must be unique ignoring case, so `alice` is taken when `Alice` is in `taken`: people were signing up as look-alikes of other users.

Do step 1 only for now, then stop. I'll come back for step 2.
