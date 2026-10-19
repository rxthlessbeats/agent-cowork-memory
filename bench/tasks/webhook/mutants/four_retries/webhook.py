"""Webhook calls to our partners: order created (POST), order status (GET), ping (HEAD)."""

import time
from urllib.request import Request, urlopen

# Only GET and HEAD are retried: a retried POST once charged a customer twice.
RETRIED = {"GET", "HEAD"}
RETRIES = 4
WAIT = 2


def http_call(method, url, body):
    """Make one call and return the response status. Raises OSError (urlopen's URLError) when it fails."""
    with urlopen(Request(url, data=body, method=method), timeout=10) as response:
        return response.status


def send(method, url, body=None, transport=http_call, sleep=time.sleep):
    retries = RETRIES if method in RETRIED else 0
    for attempt in range(retries + 1):
        try:
            return transport(method, url, body)
        except OSError:
            if attempt == retries:
                raise
            sleep(WAIT)
