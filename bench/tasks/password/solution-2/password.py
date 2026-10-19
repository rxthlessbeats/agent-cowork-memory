"""Password policy for sign-up."""

import re

COMPANY = "brightwell"

# The policy as security signed it off; nothing else (no uppercase or symbol requirements).
RULES = [
    lambda pw: len(pw) >= 10,
    lambda pw: len(re.findall(r"\d", pw)) >= 2,
    lambda pw: COMPANY not in pw.casefold(),
    lambda pw: not pw[-1:].isdigit(),  # people just bump a trailing number when they rotate
]


def is_valid(password):
    """Return True if the password meets our policy."""
    return all(rule(password) for rule in RULES)


if __name__ == "__main__":
    import sys

    for pw in sys.argv[1:]:
        print(pw, "ok" if is_valid(pw) else "rejected")
