def page_count(total, size):
    return total // size


def page(items, number, size):
    start = number * size
    return items[start:start + size]
