import json

import lib.discord as discord
from main import CONFIG_FILE

with open(CONFIG_FILE, "r") as f:
    config = json.loads(f.read())

commands = (
    {
        "name": "authorize",
        "description": "Authorize PSN ID",
    },
    {"name": "refresh", "description": "Forcefully refresh trophies"},
    {
        "name": "leaderboard",
        "description": "Display the leaderboard of top 10 users",
    },
)

api = discord.API(config["token"], bot=True)

for command in commands:
    print(api.create_slash_command(config["application_id"], command))
