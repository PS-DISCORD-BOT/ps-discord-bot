import urllib.request
import json


def perform_request(url, headers={}):
    if headers.get("User-Agent") is None:
        # Some APIs don't like an unset user-agent
        headers = {**headers, "User-Agent": "python-requests/2.28.1"}

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode("utf-8"))
