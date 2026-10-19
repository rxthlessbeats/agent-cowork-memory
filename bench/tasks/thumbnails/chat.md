Let's do TASK.md in two steps.

Step 1: add `parse_size(text)` to thumbs.py: "800x600" gives (800, 600). Accept a capital X too, ignore spaces at either end, and raise ValueError unless it's two positive whole numbers.

Step 2, for later: `thumb_spec(width, height)`. The README is out of date on thumbnails, so go by what I say here. The new gallery grid shows them at 160x120, so that's the size now, and they're JPEG at quality 85: PNG thumbnails of photos were far too big. Keep the whole image: scale it to fit inside 160x120 and pad the rest with white, with the image in the middle. Never crop; the square crops kept cutting people's heads off. And never upscale an image smaller than that: it stays at its own size, in the middle, with white around it. Leave the README alone; I'll rewrite it once step 2 is done.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how thumbs.py works today, function by function, and what could go wrong with the file names it gets: uppercase extensions, names without an extension, a name like "photo.png.exe", and so on. Don't change anything.

---

Add a docstring to parse_size with an example.

---

Add a test file, test_thumbs.py, using unittest, for parse_size: a plain size, a capital X with spaces at the ends, and two bad inputs.

---

Explain in detail how EXIF orientation works in phone photos, and why a photo stored as 4000x3000 can show up as portrait. Don't change anything.

---

Explain in detail how str.split, str.partition and regular expressions compare for parsing a size like "800x600", and when each is the better choice. Don't change the code.

---

Rename ALLOWED to IMAGE_EXTENSIONS everywhere it's used.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in thumbs.py right now, with an example call and its result.

---

Add `extension(name)`: the lowercase extension of a file name without the dot, or "" when there isn't one, and a test for it.

---

Explain in detail how you would serve the thumbnails over HTTP so browsers cache them: Cache-Control, ETag, and what to do when a thumbnail changes. Don't implement it.

---

Explain in detail why an upload's extension isn't enough to know it's really an image, and how checking the file's first bytes works. Don't change anything.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
