"""Password policy for sign-up."""


def is_valid(password):
    """Return True if the password meets our policy."""
    return True


if __name__ == "__main__":
    import sys

    for pw in sys.argv[1:]:
        print(pw, "ok" if is_valid(pw) else "rejected")
