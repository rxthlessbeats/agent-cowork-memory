# Metrics exporter

`render()` in exporter/main.py returns the text Prometheus scrapes from the shop: each metric's TYPE line, then the metric with its labels and value.

Step 1: `escape(value)` in exporter/textfmt.py, escaping a label value for the Prometheus text format: a backslash becomes `\\`, a double quote `\"`, and a newline `\n`.

Step 2: we are moving to the eu-west region. Every metric gets the label `region="eu-west"`, and the `host` label goes: no metric carries it any more.
