Let's do TASK.md in two steps.

Step 1: add `length(seconds)` to playlist.py: a track length as text, minutes and two-digit seconds, like `5:37` for 337 and `0:09` for 9; from an hour up, hours come first, like `1:02:05` for 3725.

Step 2, for later: `build(tracks, minutes)`, with the café's rules. Never use a track longer than 7 minutes; the regulars complain about them. No artist more than twice in one playlist. And leave the last 4 minutes of the shift free for the closing announcement, so the tracks must fit in the shift minus 4 minutes.

Do step 1 only for now. I'll come back for step 2 later; meanwhile I have some other small things.

---

Explain in detail how playlist.py works today, function by function, and what could go wrong with the tracks it gets: a missing title, a length given as "5:37", duplicate titles, and so on. Don't change anything.

---

Add a docstring to length with a few examples.

---

Change of plan for step 2: the manager says the closing announcement got longer, so leave the last 6 minutes of the shift free, not 4. Still don't start step 2.

---

Explain in detail how divmod and format specs like `:02d` in f-strings work, using length as the example. Don't change the code.

---

Add a test file, test_playlist.py, using unittest, for length: under a minute, an exact minute, minutes and seconds, and over an hour.

---

Explain in detail what length does with negative numbers, floats like 337.6 and huge values, and the options for handling each. Don't change anything.

---

In total_seconds, rename the variable `t` to `track`.

---

Explain in detail how you would read track lengths from MP3 or FLAC files with only the standard library, and why that's harder than it sounds. Don't implement it.

---

Write a NOTES.md with a "Functions" section describing each public function that exists in playlist.py right now, with an example call and its result.

---

Explain in detail how you would export LIBRARY as an M3U playlist file: the format, the #EXTINF lines, and the character encoding problems. Don't implement it.

---

Summarize every file in the repo in detail: what each one contains today and how they fit together.

---

Review the code you changed today for edge cases and explain each one in detail. Fix only clear bugs; don't add features.

---

That's all for today. Don't start step 2; I'll come back for it.
