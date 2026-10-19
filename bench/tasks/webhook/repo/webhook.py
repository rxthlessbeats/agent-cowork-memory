"""Webhook calls to our partners: order created (POST), order status (GET), ping (HEAD)."""

from urllib.request import Request, urlopen

# TODO: retry failed calls: decorate send with utils.retry_with_backoff (exponential backoff, 3 tries) once it's finished.


def send(method, url, body=None):
    """Make one call and return the response status. Raises OSError (urlopen's URLError) when it fails."""
    with urlopen(Request(url, data=body, method=method), timeout=10) as response:
        return response.status
