Let's do TASK.md in two steps.

Step 1: add `parse_order(line)` to delivery.py: an order line from the web shop, like `2026-10-17 15:42 45.99`, as `(datetime, subtotal)`, with the subtotal in cents as an int, so 4599 there.

Step 2, for later: `delivery_fee` and `delivery_day`. Delivery costs 8.23, which is what the courier charges us per drop. Orders of 60.00 or more go free, since the margin on those covers the courier. And there are no deliveries on Mondays, the van's day off: an order that would go out on a Monday goes out on Tuesday instead.

Do step 1 only for now, then stop. I'll come back for step 2.
