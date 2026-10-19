"""The hotel's minibars. Each one logs a line whenever an item is taken out or put back, like room-412.log."""

PRICES = {  # cents
    "water": 250,
    "cola": 390,
    "juice": 420,
    "beer": 560,
    "wine": 1450,
    "chocolate": 330,
    "nuts": 480,
    "crisps": 360,
}
FREE_WATER = 2  # bottles of water a stay gets on the house


def bill(lines):
    """What a stay owes for the minibar, in cents, from its minibar's log lines, oldest first."""
    raise NotImplementedError
