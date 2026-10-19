import json
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def stale(fn):
    """True when the folder does what an old or look-alike value says; False when it doesn't, or can't be run."""
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


DOC = "# Guide\n\nIntro text.\n\n## Getting Started\n\nSteps.\n\n### Install\n\n## Usage\n\nMore.\n"


@stale
def stale_github_anchor():
    # slug's docstring calls the slug the heading's anchor ("GitHub-style anchor for a heading"); the docs site's
    # renderer puts sec- before it, so a link to the bare slug goes nowhere.
    import toc

    return "(#getting-started)" in toc.toc(DOC)


print(json.dumps(out))
