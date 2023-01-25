import discord
import roles


def run(token, refresh_interval_hours, roles_threshold):
    api = discord.API(token, bot=True)
    roles = roles.Roles(api, roles_threshold)

    while True:
        time.sleep(refresh_interval_hours * 60 * 60)
