# Gallery

Users upload images, and the gallery shows a thumbnail of each. The resizer service makes the thumbnails; thumbs.py only works out what it should make.

## Thumbnails

Thumbnails are 128x128 PNG. The image is cropped to a square from its middle, then scaled to 128x128, so smaller images are scaled up.

`thumb_spec(width, height)` returns the resizer's spec for an image of that size, as a dict:

- `size`: the thumbnail's (width, height)
- `format`: "PNG" or "JPEG"
- `quality`: the JPEG quality, or None for PNG
- `crop`: the (left, top, right, bottom) box of the image to keep, or None to keep all of it
- `scaled`: the (width, height) the kept part is scaled to
- `padding`: the (left, top, right, bottom) border around the scaled image, in pixels
- `background`: the border's color, like "black", or None when there's no border
