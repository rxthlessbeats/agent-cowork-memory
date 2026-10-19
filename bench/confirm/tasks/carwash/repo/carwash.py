"""The self-service jet wash bays: the bay controller's session log, and charging customers' cards."""


def sessions(path):
    """Every session in the bay controller's log at path, one parsed line each."""
    with open(path) as log:
        return [parse_log(line) for line in log if line.strip()]
