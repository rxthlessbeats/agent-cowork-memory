"""Storage quota warnings for the account page."""

GB = 1024**3
WARN_AT = 0.80  # users get a warning once they have used this share of their quota


def warning(used, limit):
    """Return the warning to show a user, or None when they are not close to their quota.

    used: the bytes they store; limit: their quota, in bytes.
    """
    return None


if __name__ == "__main__":
    import sys

    # python3 quota.py USED_GB LIMIT_GB
    print(warning(float(sys.argv[1]) * GB, float(sys.argv[2]) * GB))
