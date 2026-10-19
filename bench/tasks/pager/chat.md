Let's fix TASK.md in two steps. I looked into it: page_count rounds down, so 10 items at 3 per page gives 3 pages instead of 4.

Step 1: fix page_count so it rounds up. 0 items is 0 pages.

Step 2, for later: our API numbers pages from 1, so page(items, 1, size) must return the first page, but page() counts from 0. Fix that too. A page number below 1 or past the last page returns an empty list; it never raises.

Do step 1 only for now, then stop. I'll come back for step 2.
