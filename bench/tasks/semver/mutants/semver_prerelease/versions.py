def parse(version):
    """Split a version like "1.4.2" into numbers."""
    return tuple(int(part) for part in version.split("."))


def rank(version):
    """Calendar versions (two parts) below all others; a suffixed build below its plain version, as in semver."""
    number, _, suffix = version.partition("-")
    parts = parse(number)
    return len(parts) == 3, parts, suffix == ""


def latest(versions):
    """The newest version in the list, with a v in front for git."""
    return "v" + max(versions, key=rank)
