"""Helpers for email addresses."""


def local_part(address):
    """"Ann@Corner.Example" -> "Ann"."""
    return address.rsplit("@", 1)[0]


def domain(address):
    """The part after the last @, lowercased: "Ann@Corner.Example" -> "corner.example"."""
    return address[address.rindex("@") + 1 :].lower()
