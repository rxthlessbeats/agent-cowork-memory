"""Password policy for sign-up."""


def is_valid(password):
    """Return True if the password meets our policy."""
    return (
        len(password) >= 10
        and any(c.isdigit() for c in password)
        and "brightwell" not in password.lower()
        and not password[-1].isdigit()
    )


if __name__ == "__main__":
    import sys

    for pw in sys.argv[1:]:
        print(pw, "ok" if is_valid(pw) else "rejected")
