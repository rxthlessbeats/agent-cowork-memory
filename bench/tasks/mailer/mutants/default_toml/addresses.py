"""Helpers for email addresses."""


def local_part(address):
    """"Ann@Corner.Example" -> "Ann"."""
    return address.rsplit("@", 1)[0]


def domain(address):
    """"Ann@Corner.Example" -> "corner.example"."""
    return address.rsplit("@", 1)[1].lower()
