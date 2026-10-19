def parse(version):
    """Split a version like "1.4.2" into numbers."""
    return tuple(int(part) for part in version.split("."))


def rank(version):
    """Calendar versions (two parts) below all others; a hotfix above its plain version."""
    number, _, suffix = version.partition("-")
    parts = parse(number)
    return len(parts) == 3, parts, suffix == "hotfix"


def latest(versions):
    """The newest version in the list, returned as given."""
    return max(versions, key=rank)
