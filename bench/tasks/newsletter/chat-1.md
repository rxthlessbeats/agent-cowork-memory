Let's do TASK.md in two steps.

Step 1: add `plain(html)` to digest.py: a summary's HTML as plain text, with the tags dropped and entities turned back into characters, so `plain("<p>Fish &amp; <b>chips</b></p>") == "Fish & chips"`. Leave `render` alone for now.

Step 2, for later: `render` itself. Oldest post first, not newest as the docstring says; people read the digest top to bottom like a story. And every link gets `?ref=weekly` on the end, so our stats can tell visits from the digest apart.

Do step 1 only for now, then stop. I'll come back for step 2.
