def page_count(total, size):
    return -(-total // size)


def page(items, number, size):
    if number < 1 or number > page_count(len(items), size):
        raise IndexError(f"no page {number}")
    start = (number - 1) * size
    return items[start:start + size]
