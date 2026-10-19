Let's do TASK.md in two steps.

Step 1: add `percent_off(code)` to checkout.py. It looks the code up in `CODES`, ignoring case and spaces around it, so `percent_off(" spring10 ")` is 10; no code or an unknown code gives 0. Don't use it in `total` yet.

Step 2, for later: marketing's rules for the codes. A code only works on a subtotal of 30.00 or more; below that the customer pays the full subtotal. Lines whose SKU starts with `GIFT-` are gift cards and never get a discount. And no code ever takes more than 20.00 off.

Do step 1 only for now, then stop. I'll come back for step 2.
