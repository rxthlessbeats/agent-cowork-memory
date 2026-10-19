# Mailer

Step 1: `domain(address)` in addresses.py, giving the part of an address after the @, lowercased: "Ann@Corner.Example" gives "corner.example".

Step 2: the shop's mail goes out from noreply@corner.example, and replies go to support@corner.example (a Reply-To header).
