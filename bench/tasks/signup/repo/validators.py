"""Checks for the sign-up form.

Usernames are 3 to 20 characters, letters and digits only, and case-sensitive:
"Alice" and "alice" are two different users.
"""


def valid_email(address):
    """Whether an email address looks usable: something, an @, then a domain."""
    local, _, domain = address.partition("@")
    return bool(local and domain)
