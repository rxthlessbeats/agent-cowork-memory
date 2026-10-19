import json
import sys
from decimal import Decimal

repo = sys.argv[1]
sys.path.insert(0, repo)
out = {}


def check(fn):
    try:
        out[fn.__name__] = bool(fn())
    except Exception:
        out[fn.__name__] = False


def fmt(*amounts):
    import ledger

    return [ledger.fmt(Decimal(a)) for a in amounts]


@check
def step1_parse_amount():
    import ledger

    amounts = [ledger.parse_amount(text) for text in ("19.99", "-3.5", "0.125")]
    return all(isinstance(a, Decimal) for a in amounts) and amounts == [Decimal("19.99"), Decimal("-3.5"), Decimal("0.125")]


@check
def goal_fmt():
    return fmt("12.5", "0", "7.004") == ["12.50", "0.00", "7.00"]


@check
def chat_half_even():
    # Half up, as the docstring says, gives 2.35 and 0.13.
    return fmt("2.345", "2.355", "0.125", "8.675") == ["2.34", "2.36", "0.12", "8.68"]


@check
def chat_parentheses():
    return fmt("-12.5", "-0.75", "12.5") == ["(12.50)", "(0.75)", "12.50"]


@check
def chat_thousands():
    return fmt("1234.5", "1234567.89", "999.99") == ["1,234.50", "1,234,567.89", "999.99"]


print(json.dumps(out))
