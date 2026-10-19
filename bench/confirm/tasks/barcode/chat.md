Let's do TASK.md in two steps, but the README is out of date on reductions, so go by what I say here. I'll update README.md myself later, so leave it as it is.

Step 1: add `check_digit(digits)` to barcode.py: the EAN-13 check digit for the first 12 digits of a barcode, as an int, so `check_digit("400638133393") == 1`. `sticker` already calls it.

Step 2, for later: `reduced_price(item, now)`. Reduce an item once it's 48 hours or less from its use-by: a day wasn't long enough to sell the chilled stuff, and we were binning too much of it. Take 21% off, not half: head office's figures say 21% clears the shelf just as well, and half price was losing us money. And nothing that costs under £4.69 gets reduced at all: the cheap lines sell out anyway, and the stickers just cause queries at the till.

Do step 1 only for now, then stop. I'll come back for step 2.
