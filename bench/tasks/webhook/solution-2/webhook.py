"""Webhook calls to our partners: order created (POST), order status (GET), ping (HEAD)."""

import time
from urllib.request import Request, urlopen

# TODO: retry failed calls: decorate send with utils.retry_with_backoff (exponential backoff, 3 tries) once it's finished.


def urlopen_status(method, url, body):
    """Make one call and return the response status. Raises OSError (urlopen's URLError) when it fails."""
    with urlopen(Request(url, data=body, method=method), timeout=10) as response:
        return response.status


def send(method, url, body=None, *, transport=urlopen_status, sleep=time.sleep):
    """Make the call and return the response status. A failed GET or HEAD is tried again 2 seconds later, up to 4
    attempts in all; any other method gets one attempt, since a retried POST once charged a customer twice. Raises
    the last attempt's OSError when every attempt fails."""
    attempts_left = 4 if method in ("GET", "HEAD") else 1
    while True:
        attempts_left -= 1
        try:
            return transport(method, url, body)
        except OSError:
            if not attempts_left:
                raise
        sleep(2)
