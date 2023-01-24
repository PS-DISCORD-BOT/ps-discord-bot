import urllib.request
from dataclasses import fields


# Convert a dict to a dataclass with common fields
def dict_cls(d, cls):
    field_names = set(f.name for f in fields(cls))
    filtered_dict = {k: v for k, v in d.items() if k in field_names}

    return cls(**filtered_dict)


def perform_request(url, headers={}):
    if headers.get("User-Agent") is None:
        # Some APIs don't like an unset user-agent
        headers = {**headers, "User-Agent": "python-requests/2.28.1"}

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")
