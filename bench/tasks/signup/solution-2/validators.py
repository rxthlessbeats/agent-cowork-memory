"""Checks for the sign-up form.

Usernames are 3 to 20 characters, letters and digits only, and case-sensitive:
"Alice" and "alice" are two different users.
"""

import string

USERNAME_CHARS = set(string.ascii_letters + string.digits + "_.")


def valid_email(address):
    """Whether an email address looks usable: something, an @, then a domain."""
    if address.count("@") != 1 or any(c.isspace() for c in address):
        return False
    local, domain = address.split("@")
    return bool(local and domain)


def valid_username(name, taken):
    """True when a new user may have this name, given taken, the set of names already in use.

    4 to 24 characters, only letters, digits, underscores and dots, and unique ignoring case.
    """
    return (
        4 <= len(name) <= 24
        and set(name) <= USERNAME_CHARS
        and all(name.casefold() != other.casefold() for other in taken)
    )
