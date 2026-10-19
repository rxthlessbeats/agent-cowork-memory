# Receipts

Step 1: `item_count(order)` in orders.py: how many items an order has, counting quantities, so an order of 2 mugs and a teapot has 3.

Step 2: the shop's receipts switch to the new layout, and show VAT. After the subtotal comes a line like `VAT 21%: 2.10` (for a 10.00 subtotal): 21% of the subtotal, rounded half up to the cent. The total includes it.
