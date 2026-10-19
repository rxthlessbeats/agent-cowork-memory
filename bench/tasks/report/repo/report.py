import csv
import sys


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main(argv):
    print("usage: python report.py summary [file]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
