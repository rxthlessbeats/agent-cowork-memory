# Reduced stickers

barcode.py makes the barcodes for the shop's yellow reduced-price stickers.

## Reductions

An item is reduced once it is within 24 hours of its use-by. Reduced items are half price. Items under £1 are never reduced: it isn't worth the sticker. Anything dearer than the manager limit (`MANAGER_LIMIT` in config.py) is left for a manager to price by hand.

## Stickers

A sticker's barcode is an EAN-13: `29`, the item's 5-digit code, the reduced price in pence as 5 digits, then the check digit.
