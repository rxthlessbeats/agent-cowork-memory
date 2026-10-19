"""Webhook calls to our partners: order created (POST), order status (GET), ping (HEAD)."""

import time
from urllib.request import Request, urlopen

from utils import retry_with_backoff

# Only GET and HEAD are retried, with the finished utils.retry_with_backoff: 4 tries, from 2 seconds.
RETRIED = {"GET", "HEAD"}


def http_call(method, url, body):
    """Make one call and return the response status. Raises OSError (urlopen's URLError) when it fails."""
    with urlopen(Request(url, data=body, method=method), timeout=10) as response:
        return response.status


def send(method, url, body=None, transport=http_call, sleep=time.sleep):
    if method in RETRIED:
        return retry_with_backoff(tries=4, delay=2.0)(transport)(method, url, body)
    return transport(method, url, body)
