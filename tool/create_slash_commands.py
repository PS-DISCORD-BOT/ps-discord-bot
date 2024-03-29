import json
from time import sleep

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
        "name": "howtolink",
        "description": "Instructions to link with PSNProfiles",
    },
    {
        "name": "rank",
        "description": "View rank and trophies",
        "options": [
            {
                "name": "user",
                "description": "The user whose rank is to be fetched",
                "type": 6,  # USER
                "required": False,
            }
        ],
    },
    {
        "name": "leaderboard",
        "description": "Display the leaderboard of user points",
    },
    {
        "name": "platinum_leaderboard",
        "description": "Display the leaderboard of user trophies",
    },
)

api = discord.API(config["token"], bot=True)

for command in commands:
    print(api.create_slash_command(config["application_id"], command))
    sleep(1)
