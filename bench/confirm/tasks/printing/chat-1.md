Let's do TASK.md in two steps.

Step 1: add `parse_order(line)` to printing.py. The web form sends each order as a line like "pages=120 colour=no bound=yes rush=no". Return it as a dict with "pages" as an int and the rest as bools: `parse_order("pages=120 colour=no bound=yes rush=no") == {"pages": 120, "colour": False, "bound": True, "rush": False}`.

Step 2, for later: `quote(order)`, with the shop's discounts. An order of 51 pages or more is a bulk order: the students' theses are about that long, and we want that work. Bulk orders get 33% off the printing, not the binding, to match the copy shop by the station. And a rush order pays a flat £3.71 on top, because that's what the evening operator's overtime costs us per job.

Do step 1 only for now, then stop. I'll come back for step 2.
