import urllib.request


def perform_request(url, headers={}):
    if headers.get("User-Agent") is None:
        # Some APIs don't like an unset user-agent
        headers = {**headers, "User-Agent": "python-requests/2.28.1"}

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")
