def page_count(total, size):
    return -(-total // size)


def page(items, number, size):
    if number < 0 or number >= page_count(len(items), size):
        return []
    start = number * size
    return items[start:start + size]
