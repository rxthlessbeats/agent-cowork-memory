"""Webhook calls to our partners: order created (POST), order status (GET), ping (HEAD)."""

import time
from urllib.request import Request, urlopen

from utils import retry_with_backoff


def http_call(method, url, body):
    """Make one call and return the response status. Raises OSError (urlopen's URLError) when it fails."""
    with urlopen(Request(url, data=body, method=method), timeout=10) as response:
        return response.status


# As the TODO said: retried with utils.retry_with_backoff, exponential backoff, 3 tries.
@retry_with_backoff()
def send(method, url, body=None, transport=http_call, sleep=time.sleep):
    return transport(method, url, body)
