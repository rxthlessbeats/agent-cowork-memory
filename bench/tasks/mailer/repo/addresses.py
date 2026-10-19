"""Helpers for email addresses."""


def local_part(address):
    """"Ann@Corner.Example" -> "Ann"."""
    return address.rsplit("@", 1)[0]
