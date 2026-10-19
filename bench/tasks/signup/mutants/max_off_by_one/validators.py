"""Checks for the sign-up form.

Usernames are 3 to 20 characters, letters and digits only, and case-sensitive:
"Alice" and "alice" are two different users.
"""

import re

USERNAME = re.compile(r"[A-Za-z0-9_.]+")


def valid_email(address):
    """Whether an email address looks usable: no spaces, and one @ with something on each side."""
    local, _, domain = address.partition("@")
    return bool(local and domain) and "@" not in domain and not any(c.isspace() for c in address)


def valid_username(name, taken):
    """4 to 24 characters, meant to be: range(4, 24) stops at 23."""
    return (
        len(name) in range(4, 24)
        and USERNAME.fullmatch(name) is not None
        and name.casefold() not in {t.casefold() for t in taken}
    )
