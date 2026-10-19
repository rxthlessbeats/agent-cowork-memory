"""Webhook calls to our partners: order created (POST), order status (GET), ping (HEAD)."""

import time
from urllib.request import Request, urlopen

# Every method is retried, POST included.
ATTEMPTS = 4
WAIT = 2


def http_call(method, url, body):
    """Make one call and return the response status. Raises OSError (urlopen's URLError) when it fails."""
    with urlopen(Request(url, data=body, method=method), timeout=10) as response:
        return response.status


def send(method, url, body=None, transport=http_call, sleep=time.sleep):
    for attempt in range(1, ATTEMPTS + 1):
        try:
            return transport(method, url, body)
        except OSError:
            if attempt == ATTEMPTS:
                raise
            sleep(WAIT)
