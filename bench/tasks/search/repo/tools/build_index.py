"""Builds index/words.json, the word index search.find reads, from docs/*.txt.

python3 tools/build_index.py prints the index; python3 tools/build_index.py --write saves it.
"""

import glob
import json
import os
import re
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)


def synonyms():
    """The synonym groups in tools/synonyms.txt: one per line, words separated by commas."""
    with open(os.path.join(TOOLS, "synonyms.txt")) as f:
        lines = [line.split("#")[0] for line in f]
    return [{word.strip().lower() for word in line.split(",")} - {""} for line in lines if line.strip()]


def build():
    index = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "docs", "*.txt"))):
        name = os.path.basename(path)[: -len(".txt")]
        with open(path) as f:
            for word in re.findall(r"[a-z]+", f.read().lower()):
                index.setdefault(word, set()).add(name)
    # Every word of a synonym group finds the documents that have any of its words.
    for group in synonyms():
        docs = set().union(*(index.get(word, set()) for word in group))
        for word in group:
            index[word] = docs
    return {word: sorted(docs) for word, docs in index.items()}


def main():
    text = json.dumps(build(), sort_keys=True) + "\n"
    if "--write" in sys.argv[1:]:
        with open(os.path.join(ROOT, "index", "words.json"), "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
