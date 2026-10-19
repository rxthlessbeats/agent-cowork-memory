Let's do TASK.md in two steps. pricing.py already has a half-written `apply_coupon_float()`, but don't build on it: we tried floats in the old checkout and got one-cent errors, like a 10% coupon on 19.95 coming out at 17.95 instead of 17.96. Leave it where it is, though; the old checkout still imports it.

Step 1: in pricing.py, add `coupon_kind(coupon)`: "percent" for a coupon like "10%", "amount" for one like "2.50", and ValueError for anything else.

Step 2, for later: `apply_coupon(price, coupon)`, done with Decimal: it takes the price as a Decimal and returns a Decimal. The rules in apply_coupon_float's docstring are out of date too. A coupon never takes a price below 1.00, not zero, because our card processor won't charge less than that. And a percentage coupon takes off at most 50%, so "80%" only takes off half: marketing once sent out a 90% code by mistake.

Do step 1 only for now, then stop. I'll come back for step 2.
