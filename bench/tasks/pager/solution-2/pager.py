def page_count(total, size):
    full, rest = divmod(total, size)
    return full + bool(rest)


def page(items, number, size):
    """Page `number` of items, numbered from 1 like our API; [] when there is no such page."""
    if not 1 <= number <= page_count(len(items), size):
        return []
    return items[(number - 1) * size : number * size]
