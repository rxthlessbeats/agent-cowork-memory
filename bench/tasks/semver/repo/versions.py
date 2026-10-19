def parse(version):
    """Split a version like "1.4.2" into numbers."""
    raise NotImplementedError


def latest(versions):
    """The newest version in the list, returned as given."""
    return max(versions)
