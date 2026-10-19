"""Export formats. Each exporter is a module with render(orders) -> str, imported the first time it's asked for."""

import importlib

# Format name -> dotted path of the module that renders it.
REGISTRY = {
    "csv": "exporters.csv_writer",
    "json": "exporters.json_out",
}


def get(name):
    """The exporter module registered under `name`."""
    return importlib.import_module(REGISTRY[name])
