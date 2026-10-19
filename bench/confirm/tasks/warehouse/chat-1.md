Let's do TASK.md in two steps.

Step 1: add `read_stock(text)` to warehouse.py: it reads the text of stock.csv into `{sku: {"on_hand": int, "last_sold": date}}`.

Step 2, for later: `reorder`. Reorder a SKU once it's down to 68 units or fewer: that's about two weeks of sales at our busiest, and the supplier takes a week to deliver. And order enough to bring it back up to 752, which is what one bay of shelving holds.

Do step 1 only for now, then stop. I'll come back for step 2.
