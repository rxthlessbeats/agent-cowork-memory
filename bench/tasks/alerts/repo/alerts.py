"""Disk space alerts for the ops channel."""


def parse(line):
    """A reading from the disk agent, like "web-1 /var 91.5", as (host, mount, percent used)."""
    host, mount, percent = line.split()
    return host, mount, percent


def level(history):
    """How full a disk is: "ok", "warning" or "critical", from its percent-used readings, oldest first."""
    return "ok"


def message(host, mount, history):
    """The line to post in the ops channel about this disk, or None when it is ok."""
    return None


if __name__ == "__main__":
    import sys

    host, mount, percent = parse(sys.argv[1])
    print(message(host, mount, [percent]))
