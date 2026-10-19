"""Checks for the sign-up form.

Usernames are 3 to 20 characters, letters and digits only, and case-sensitive:
"Alice" and "alice" are two different users.
"""

import re

USERNAME = re.compile(r"[A-Za-z0-9]{3,20}")


def valid_email(address):
    """Whether an email address looks usable: no spaces, and one @ with something on each side."""
    local, _, domain = address.partition("@")
    return bool(local and domain) and "@" not in domain and not any(c.isspace() for c in address)


def valid_username(name, taken):
    """As the module docstring says: 3 to 20 letters and digits, and case-sensitive."""
    return USERNAME.fullmatch(name) is not None and name not in taken
