# Charge points

The company's public charge points for electric cars. `session_cost` in charging.py works out what a driver pays for a charging session, in cents.

## Pricing

Energy is charged at `PRICE_PER_KWH`, in charging.py.

A car that stays plugged in more than 30 minutes after it's full pays an idle fee of 5.00, so that the charger is free for the next driver.

Members get 10% off the energy.
