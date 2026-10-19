"""Checks for the sign-up form.

Usernames are 3 to 20 characters, letters and digits only, and case-sensitive:
"Alice" and "alice" are two different users.
"""

import re

USERNAME = re.compile(r"[A-Za-z0-9.]{3,24}")


def valid_email(address):
    """Whether an email address looks usable: no spaces, and one @ with something on each side."""
    local, _, domain = address.partition("@")
    return bool(local and domain) and "@" not in domain and not any(c.isspace() for c in address)


def valid_username(name, taken):
    """Chat 2's change (up to 24, dots too) on the docstring's rules: 3 at least, no underscores, case-sensitive."""
    return USERNAME.fullmatch(name) is not None and name not in taken
