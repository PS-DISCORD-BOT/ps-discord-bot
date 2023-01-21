import json
from dataclasses import dataclass

from utils import perform_request

API_BASE = "https://discord.com/api/v10"


@dataclass
class Connection:
    type: str
    id: str
    name: str


@dataclass
class User:
    id: str
    # ..., not required


class API:
    def __init__(self, token):
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_connections(self):
        resp = json.loads(
            perform_request(API_BASE + "/users/@me/connections", self.headers)
        )

        return [
            Connection(conn["type"], conn["id"], conn["name"]) for conn in resp
        ]

    def get_user(self):
        resp = json.loads(
            perform_request(API_BASE + "/users/@me", self.headers)
        )

        return User(resp["id"])
