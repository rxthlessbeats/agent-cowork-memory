"""Storage quota warnings for the account page."""
import math

GB = 1024**3
WARN_AT = 0.88  # users get a warning once they have used this share of their quota


def percent(used, limit):
    """How much of the quota is used, as a percentage: percent(GB, 4 * GB) == 25.0.
    A limit of 0 means the user has no quota: 0.0."""
    return used * 100 / limit if limit else 0.0


def warning(used, limit):
    """Return the warning to show a user, or None when they are not close to their quota.

    used: the bytes they store; limit: their quota, in bytes.
    """
    if not limit or used < WARN_AT * limit:
        return None
    return f"You have used {math.ceil(percent(used, limit))}% of your storage."


if __name__ == "__main__":
    import sys

    # python3 quota.py USED_GB LIMIT_GB
    print(warning(float(sys.argv[1]) * GB, float(sys.argv[2]) * GB))
