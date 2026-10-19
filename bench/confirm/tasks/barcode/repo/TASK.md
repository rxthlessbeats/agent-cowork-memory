# Reduced stickers

Staff work out reduced prices in their heads, and the sticker printer prints whatever they type. Add `reduced_price(item, now)` to barcode.py, as README.md describes: the price in pence for an item's reduced sticker, or None when it gets no sticker. An item is a dict with "code", "price" (in pence) and "use_by" (a datetime). Anything over the manager limit is left for a manager.
