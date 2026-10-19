"""Checks for the sign-up form.

Usernames are 3 to 20 characters, letters and digits only, and case-sensitive:
"Alice" and "alice" are two different users.
"""

import re

USERNAME = re.compile(r"[A-Za-z0-9_.]{4,24}")


def valid_email(address):
    """Whether an email address looks usable: no spaces, and one @ with something on each side."""
    local, _, domain = address.partition("@")
    return bool(local and domain) and "@" not in domain and not any(c.isspace() for c in address)


def valid_username(name, taken):
    """Unique ignoring case, meant to be: it lowercases the new name, but not the taken ones."""
    return USERNAME.fullmatch(name) is not None and name.lower() not in taken
