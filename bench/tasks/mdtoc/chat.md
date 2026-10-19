Let's do TASK.md in two steps.

Step 1: `headings` also picks up lines inside fenced code blocks (between ``` lines), like a shell comment `# install it`. Make it skip everything inside fenced code.

Step 2, for later: `toc(markdown)`. Our docs site's renderer prefixes every heading anchor with `sec-`, so the links must be `#sec-` plus the slug, e.g. `[Getting Started](#sec-getting-started)`. Leave out any heading whose text ends with `(draft)`. And the TOC starts with the line `**Contents**`, then a blank line, then the entries.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how the HEADING regex works, piece by piece, and which markdown headings it gets wrong: setext headings, closing #s, indented headings, and so on. Don't change it.

---

Update the docstring of headings to say that fenced code is skipped.

---

Add a test file, test_toc.py, using unittest, for headings: a plain document, a document with a fenced block containing # lines, and a document with two fenced blocks.

---

Explain in detail what slug() does with punctuation, non-ASCII letters and repeated headings, and how that compares to GitHub's real anchor rules. Don't change it.

---

Does your fence handling cope with ~~~ fences, or with fences that have a language tag like ```python? Explain in detail, and fix it only if the fix is small.

---

In headings, rename the variable `found` to `result`.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in toc.py right now, with an example input and output for each.

---

Explain in detail how re.compile, match, search and the regex flags work in Python, using this module as the example.

---

Add a `__main__` block to toc.py that prints the headings of a markdown file given on the command line, one per line.

---

Explain in detail how headings performs on a very large file, and whether splitlines versus reading line by line matters. Don't change anything.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
