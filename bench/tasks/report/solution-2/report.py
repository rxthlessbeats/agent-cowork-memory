import csv
import sys
from collections import defaultdict


def load(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def totals(rows):
    sums = defaultdict(int)
    for row in rows:
        sums[row["category"]] += int(row["amount_cents"])
    return dict(sums)


def dollars(cents):
    whole, rest = divmod(abs(cents), 100)
    return f"{'-' if cents < 0 else ''}${whole}.{rest:02d}"


def main(argv):
    args = list(argv)
    top = None
    if "--top" in args:
        at = args.index("--top")
        top = int(args[at + 1])
        del args[at : at + 2]
    if not args or args[0] != "summary" or len(args) > 2:
        print("usage: python report.py summary [file] [--top N]", file=sys.stderr)
        return 2
    path = args[1] if len(args) == 2 else "sales.csv"
    ranked = sorted(totals(load(path)).items(), key=lambda item: item[1], reverse=True)
    for category, cents in ranked if top is None else ranked[:top]:
        print(f"{category}: {dollars(cents)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
