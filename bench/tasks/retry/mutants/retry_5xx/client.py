import time
from urllib.error import HTTPError
from urllib.request import urlopen

WAITS = [0.5, 1, 2]


def fetch(url, opener=urlopen, sleep=time.sleep):
    for attempt in range(len(WAITS) + 1):
        try:
            with opener(url) as response:
                return response.read()
        except HTTPError as err:
            # Too many requests, or any server error: worth another try.
            if (err.code != 429 and err.code < 500) or attempt == len(WAITS):
                raise
            sleep(WAITS[attempt])
