import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


FENCED = "# Setup\n\n```sh\n# install it\npip install tool\n```\n\n## Usage\n\n```\n## not a heading\n```\n\n## Done\n"

DOC = "# Guide\n\nIntro text.\n\n## Getting Started\n\nSteps.\n\n### Install\n\n## Usage\n\nMore.\n"

DRAFT = "# Guide\n\n## Usage\n\n## Roadmap (draft)\n\nIdeas.\n"


@check
def step1_skip_fences():
    import toc

    return toc.headings(FENCED) == [(1, "Setup"), (2, "Usage"), (2, "Done")]


@check
def goal_toc():
    import toc

    text = toc.toc(DOC)
    positions = [text.find(name) for name in ("Getting Started", "Install", "Usage")]
    return -1 not in positions and positions == sorted(positions)


@check
def chat_sec_anchor():
    import toc

    return "(#sec-getting-started)" in toc.toc(DOC)


@check
def chat_skip_draft():
    import toc

    text = toc.toc(DRAFT)
    return "Roadmap" not in text and "Usage" in text


@check
def chat_contents_header():
    import toc

    return toc.toc(DOC).splitlines()[:2] == ["**Contents**", ""]


print(json.dumps(out))
