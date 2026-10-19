# Bingo payouts

The caller still works the prizes out on paper. Add `payout(game)` to bingo.py. A game is a dict with `day` (a date), `cards` (how many cards were sold) and `calls` (how many numbers were called before someone got a full house). It returns a dict with `prize`, the full-house prize in cents, and `jackpot`, what the jackpot pays in cents, 0 when it isn't won. A full house in few enough calls wins the jackpot as well.
