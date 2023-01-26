import logging
import sys

import lib.discord as discord

TROPHY_CHECK = "platinum"


class Roles:
    def __init__(self, api: discord.API, roles_dict: dict):
        self.api = api

        self.roles_dict = roles_dict

        for value in self.roles_dict.values():
            if not isinstance(value, int):
                raise TypeError(f"Threshold value {value} not an int")

    def setup_roles(self, guild_id):
        # role name -> role ID
        roles_id = {}

        required_roles = set(self.roles_dict.keys())

        for role in self.api.get_guild_roles(guild_id):
            if role.name in required_roles:
                roles_id[role.name] = role.id

        # All the roles that haven't been added to Discord yet
        missing_roles = required_roles - set(roles_id.keys())

        for role in missing_roles:
            logging.info(f"Creating role {role} in guild {guild_id}")
            roles_id[role] = self.api.create_guild_role(guild_id, role).id

        return roles_id

    def update_user_roles(self, roles_id, guild_id, user_id, role_name):
        self.api.add_guild_member_role(guild_id, user_id, roles_id[role_name])

        for role, role_id in roles_id.items():
            if role != role_name:
                logging.info(
                    f"Removing role {role} from user {user_id} in guild {guild_id}"
                )
                self.api.remove_guild_member_role(guild_id, user_id, role_id)

    def sync_roles(self, guild_id, id_to_trophies):
        roles_id = self.setup_roles(guild_id)

        # {"role2": 50, "role1": 10, ...}
        roles_dict_sorted = dict(
            sorted(self.roles_dict.items(), key=lambda item: item[1])[::-1]
        )

        for user_id, trophies in id_to_trophies.items():
            max_higher_than = None

            for name, target in roles_dict_sorted.items():
                if trophies[TROPHY_CHECK] >= target:
                    max_higher_than = name
                    break

            if max_higher_than is None:
                continue

            try:
                self.update_user_roles(
                    roles_id, guild_id, user_id, max_higher_than
                )
            except Exception:
                logging.warning(
                    f"Failed to update role {max_higher_than} for user {user_id} in guild {guild_id}",
                    exc_info=sys.exc_info(),
                )
