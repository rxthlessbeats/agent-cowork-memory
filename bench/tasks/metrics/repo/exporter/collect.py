"""The shop's numbers, as (metric name, metric type, value)."""


def metrics():
    return [
        ("shop_up", "gauge", 1),
        ("shop_orders_total", "counter", 1027),
        ("shop_open_carts", "gauge", 12),
    ]
