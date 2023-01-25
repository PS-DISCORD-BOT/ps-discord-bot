import logging

import discord


class Roles:
    def __init__(self, api: discord.API, roles_dict: dict):
        self.api = api

        for key in roles_dict:
            if not isinstance(key, int):
                raise TypeError(f"Key {key} is not an int")

        self.roles_dict = roles_dict

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
            roles_id[role] = self.api.create_guild_role(guild_id, role).id

        return roles_id

    def update_user_roles(self, roles_id, guild_id, user_id, role_name):
        self.api.add_guild_member_role(guild_id, user_id, roles_id[role_name])

        for role, role_id in roles_id.items():
            if role != role_name:
                self.api.remove_guild_member_role(guild_id, user_id, role_id)

    def sync_roles(self, guild_id, id_to_trophies):
        roles_id = self.setup_roles(guild_id)

        # 50, 10, 1, ...
        targets = sorted(self.roles_dict.keys())[::-1]

        for user_id, trophies in id_to_trophies.items():
            max_higher_than = None

            for target in targets:
                if trophies >= target:
                    max_higher_than = target
                    break

            if max_higher_than is None:
                continue

            role_id = self.roles_dict[max_higher_than]

            try:
                self.update_user_roles(
                    roles_id,
                    guild_id,
                    user_id,
                    role_id,
                )
            except Exception:
                logging.warning(
                    f"Failed to update role {role_id} for user {user_id} in guild {guild_id}",
                    exc_info=sys.exc_info(),
                )
