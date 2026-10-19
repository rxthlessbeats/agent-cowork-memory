Let's do TASK.md in two steps.

Step 1: make `slugify(title)` in blog.py turn accented letters into plain ones (é becomes e, using unicodedata), lowercase everything, and turn each run of characters other than a-z and 0-9 into a single hyphen, with no hyphen at either end. So `slugify("Café Déjà Vu!")` is `cafe-deja-vu`.

Step 2, for later: add `unique_slug(title, taken)`, where `taken` is the set of slugs already in use. If the slug is taken, add `-2`, then `-3`, and so on; never random characters. A slug is at most 40 characters, suffix included: cut a longer one at a hyphen so no word is split.

Do step 1 only for now, then stop. I'll come back for step 2.
