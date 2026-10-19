# Watering

The greenhouse's drip runs on a timer, whatever the soil is like. Add `watering(bed, now)` to plants.py: how many minutes to run a bed's drip now, or 0 for none. A bed is a dict with "name", "moisture" (its latest reading, in percent) and "last_watered" (a datetime, or None if it never has been). Never water a bed again too soon after its last watering.
