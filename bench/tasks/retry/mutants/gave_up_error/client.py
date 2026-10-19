import time
from urllib.error import HTTPError
from urllib.request import urlopen

RETRY = {429, 503}
WAITS = [0.5, 1, 2]


class RetriesExhausted(Exception):
    pass


def fetch(url, opener=urlopen, sleep=time.sleep):
    for attempt in range(len(WAITS) + 1):
        try:
            with opener(url) as response:
                return response.read()
        except HTTPError as err:
            if err.code not in RETRY:
                raise
            if attempt == len(WAITS):
                raise RetriesExhausted(f"{url}: gave up after {attempt + 1} attempts") from err
            sleep(WAITS[attempt])
