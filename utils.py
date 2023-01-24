import urllib.request
from dataclasses import fields


# Convert a dict to a dataclass with common fields
def dict_cls(d, cls):
    field_names = set(f.name for f in fields(cls))
    filtered_dict = {k: v for k, v in d.items() if k in field_names}

    return cls(**filtered_dict)


def perform_request(url, method="GET", headers={}, data=None):
    if headers.get("User-Agent") is None:
        # Some APIs don't like an unset user-agent
        headers = {**headers, "User-Agent": "python-requests/2.28.1"}

    req = urllib.request.Request(
        url,
        data=bytes(data, "utf-8") if data else None,
        headers=headers,
        method=method,
    )

    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")
