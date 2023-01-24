import json
from dataclasses import dataclass

from utils import dict_cls, perform_request

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

    def perform(self, endpoint):
        return json.loads(perform_request(API_BASE + endpoint, self.headers))

    def get_connections(self):
        resp = self.perform("/users/@me/connections")

        return [dict_cls(conn, Connection) for conn in resp]

    def get_user(self):
        resp = self.perform("/users/@me")

        return dict_cls(resp, User)

    def get_guilds(self):
        resp = self.perform("/users/@me/guilds")

        return [dict_cls(guild, Guild) for guild in resp]

    def get_guild_roles(self, guild_id):
        resp = self.perform(f"/guilds/{guild_id}/roles")

        return [dict_cls(role, Role) for role in resp]

    def create_guild_role(self, guild_id):
        raise NotImplementedError

    def add_guild_member_role(self, guild_id, user_id, role_id):
        raise NotImplementedError
