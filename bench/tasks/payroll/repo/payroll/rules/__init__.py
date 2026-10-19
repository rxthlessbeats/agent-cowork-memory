"""Pay rules: pay adds up what each rule in RULES pays for the week."""

import importlib

RULES = [
    "payroll.rules.base",
    "payroll.rules.overtime",
]


def load():
    """The rule modules, in order. Each has amount(hours, rate)."""
    return [importlib.import_module(name) for name in RULES]
