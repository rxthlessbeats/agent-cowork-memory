# Cache

`Cache` in cache.py keeps string values by key, in a JSON file at the path it is given. An entry expires one hour after it is written.

    cache = Cache(".cache/cache.json")
    cache.set("user:1", "Ana")
    cache.get("user:1")  # None when missing or expired
