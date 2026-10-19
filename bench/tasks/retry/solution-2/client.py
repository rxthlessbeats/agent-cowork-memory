import time
from urllib.error import HTTPError
from urllib.request import urlopen

RETRYABLE = (429, 503)  # the vendor's word: only these are worth another try
MAX_ATTEMPTS = 4
FIRST_WAIT = 0.5


def fetch(url, opener=urlopen, sleep=time.sleep):
    wait = FIRST_WAIT
    attempts = 0
    while True:
        attempts += 1
        try:
            with opener(url) as response:
                return response.read()
        except HTTPError as err:
            if err.code not in RETRYABLE or attempts == MAX_ATTEMPTS:
                raise
        sleep(wait)
        wait *= 2
