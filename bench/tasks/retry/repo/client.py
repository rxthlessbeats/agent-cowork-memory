from urllib.request import urlopen


def fetch(url, opener=urlopen):
    with opener(url) as response:
        return response.read()
