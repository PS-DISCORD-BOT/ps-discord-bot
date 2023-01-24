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


@dataclass
class Guild:
    id: str
    name: str
    # ...


@dataclass
class Role:
    id: str
    name: str
    color: int


class API:
    def __init__(self, token, *, bot):
        self.headers = {
            "Authorization": f"Bot {token}" if bot else f"Bearer {token}"
        }

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

    def get_guilds(self):
        resp = json.loads(
            perform_request(API_BASE + "/users/@me/guilds", self.headers)
        )

        return [Guild(guild["id"], guild["name"]) for guild in resp]

    def get_guild_roles(self, guild_id):
        resp = json.loads(
            perform_request(
                API_BASE + f"/guilds/{guild_id}/roles", self.headers
            )
        )

        return [Role(role["id"], role["name"], role["color"]) for role in resp]

    def create_guild_role(self, guild_id):
        raise NotImplementedError

    def add_guild_member_role(self, guild_id, user_id, role_id):
        raise NotImplementedError
