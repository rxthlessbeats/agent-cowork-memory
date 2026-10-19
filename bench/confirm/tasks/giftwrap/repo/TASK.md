# Gift wrap

Customers want to send presents straight from the shop. Add `quote(items, message)` to giftwrap.py. Each item is a dict with `sku`, `price` (cents) and `weight` (grams), as in shop.py. It returns a dict: `wrapped`, the SKUs of the items we wrap, in order; `fee`, what the wrapping costs, in cents; and `message`, the text to print on the gift card. Big orders get their wrapping free.
