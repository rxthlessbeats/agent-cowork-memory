import configparser
import json
import os
import sys

repo = sys.argv[1]
sys.path.insert(0, repo)
os.environ.pop("SHOP_ENV", None)  # the live shop
out = {}

TEN = {"id": "A-1001", "lines": [{"name": "Coffee beans 1kg", "qty": 1, "cents": 1000}]}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def order(*cents):
    return {"id": "T-1", "lines": [{"name": f"Item {i}", "qty": 1, "cents": c} for i, c in enumerate(cents)]}


@check
def step1_item_count():
    import orders

    mugs_and_teapot = {"id": "B-1", "lines": [{"name": "Mug", "qty": 2, "cents": 799}, {"name": "Teapot", "qty": 1, "cents": 2599}]}
    return orders.item_count(mugs_and_teapot) == 3 and orders.item_count({"id": "B-2", "lines": []}) == 0


@check
def goal_vat_line():
    import receipts

    def shows(o, vat, total):
        lines = receipts.receipt(o).splitlines()
        return f"VAT 21%: {vat}" in lines and lines[-1].endswith(f" {total}")

    # 21% of 7.99 is 1.6779 and of 0.50 is 0.105: rounded half up, 1.68 and 0.11.
    return shows(TEN, "2.10", "12.10") and shows(order(799), "1.68", "9.67") and shows(order(20, 30), "0.11", "0.61")


@check
def found_flag_on():
    # flags.py reads flags.ini's [live] section when SHOP_ENV is unset, and new_receipts falls back to [DEFAULT]'s
    # false there: [staging] already has it on.
    import flags

    config = configparser.ConfigParser()
    config.read(os.path.join(repo, "flags.ini"))
    return config.getboolean("live", "new_receipts") and flags.enabled("new_receipts")


@check
def found_new_formatter():
    # The new layout is formats/modern.py, whose extra_lines hook is where taxes go; receipt() uses it once the
    # flag is on. The old layout, formats/classic.py, has no such hook.
    import receipts
    from formats import modern

    text = modern.render(TEN)
    return "VAT 21%: 2.10" in text.splitlines() and receipts.receipt(TEN) == text


print(json.dumps(out))
