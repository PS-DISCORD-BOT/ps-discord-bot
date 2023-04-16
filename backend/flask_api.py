import logging
import sys
from functools import wraps

from flask import Flask, Response, abort, g, jsonify, request
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from waitress import serve

import lib.discord as discord
from backend.shared_globals import (
    TROPHY_CHECK,
    TROPHY_COLOR_CODE,
    get_db,
    get_queue,
)
from lib.scraper import fetch_trophies

app = Flask(__name__)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "PUT",
    "Access-Control-Allow-Headers": "Content-Type",
}

RANK_REPRESENTATION = {
    1: ":first_place:",
    2: ":second_place:",
    3: ":third_place:",
    4: ":four:",
    5: ":five:",
    6: ":six:",
    7: ":seven:",
    8: ":eight:",
    9: ":nine:",
    10: ":keycap_ten:",
}

TROPHY_REPRESENTATION = {
    "platinum": ":trophy:",
    "gold": ":first_place:",
    "silver": ":second_place:",
    "bronze": ":third_place:",
}


# https://discord.com/developers/docs/interactions/receiving-and-responding#security-and-authorization
def validate_discord_request(func, *args, **kwargs):
    @wraps(func)
    def inner():
        verify_key = VerifyKey(bytes.fromhex(app.config["PUBLIC_KEY"]))

        signature = request.headers["X-Signature-Ed25519"]
        timestamp = request.headers["X-Signature-Timestamp"]

        body = request.data.decode("utf-8")

        try:
            verify_key.verify(
                f"{timestamp}{body}".encode(), bytes.fromhex(signature)
            )
        except BadSignatureError:
            abort(401, "Invalid request signature")

        return func(*args, **kwargs)

    return inner


def check_psnprofile(psn_id):
    try:
        fetch_trophies(psn_id)
        return True
    except Exception:
        logging.critical(
            f"Failed to scrape trophies for PSN user {psn_id}",
            exc_info=sys.exc_info(),
        )
        return False


def rank_users(users):
    return sorted(users, key=lambda item: item[TROPHY_CHECK], reverse=True)


def find_and_rank(users, discord_id):
    for index, user in enumerate(rank_users(users)):
        if user["discord_id"] == discord_id:
            return index + 1, user


def get_avatar(member_user):
    user_id, avatar = member_user["id"], member_user.get("avatar")

    if avatar:
        return f"{discord.CDN_BASE}/avatars/{user_id}/{avatar}.png"


def split_n(arr, n):
    out = []
    prev = 0

    while prev < len(arr):
        out.append(arr[prev : prev + n])
        prev = prev + n

    if (diff := len(arr) - sum(len(out_arr) for out_arr in out)) > 0:
        out.append(arr[-diff:])

    return out


def get_leaderboard(page_no=0):
    BATCH = 10

    descending_users = rank_users(get_db().get_all())
    pages = split_n(descending_users, BATCH)

    embed = {
        "title": f"{TROPHY_CHECK.title()} Trophy Leaderboard",
        "type": "rich",
        "color": TROPHY_COLOR_CODE,
        "fields": [],
        "footer": {
            "text": f"Page {page_no + 1} of {len(pages)}",
        },
    }

    for idx, user in enumerate(pages[page_no]):
        discord_id = user["discord_id"]
        trophies = user[TROPHY_CHECK]

        idx = (page_no * BATCH) + idx + 1
        rank_repr = (
            RANK_REPRESENTATION[idx] if idx <= BATCH else f"_**#{idx}**_"
        )

        value = f"{rank_repr} `{trophies}` <@{discord_id}>"

        embed["fields"].append({"name": "", "value": value})

    return {
        "embeds": [embed],
        "components": [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "emoji": {"id": "1067941105598988410", "name": "AL"},
                        "style": 1,
                        "custom_id": f"left_{page_no}",
                        "disabled": page_no == 0,
                    },
                    {
                        "type": 2,
                        "emoji": {"id": "1067941108568567818", "name": "AR"},
                        "style": 1,
                        "custom_id": f"right_{page_no}",
                        "disabled": (page_no + 1) == len(pages),
                    },
                ],
            }
        ],
    }


def execute_cmd_json(cmd_data, member_data):
    member_user = member_data["user"]

    cmd = cmd_data["name"]
    options = cmd_data.get("options")
    user_id = member_user["id"]

    match cmd:
        case "authorize":
            return {
                "content": "Click the button to authorize your account",
                "flags": 1 << 6,  # EPHEMERAL
                "components": [
                    {
                        "type": 1,  # Action bar
                        "components": [
                            {
                                "type": 2,  # Button
                                "label": "Authorize",
                                "style": 5,  # Link
                                "url": app.config["AUTHORIZATION_URL"],
                            }
                        ],
                    }
                ],
            }
        case "howtolink":
            return {
                "content": "**NOTE**: You must first enlist your account on https://psnprofiles.com by entering your name and hitting **Update User**. Trophies can then be refreshed with the /refresh command"
            }
        case "refresh":
            if (psn_id := get_db().get_id_to_psn(user_id)) is None:
                return {
                    "content": "It seems you haven't authorized your account yet, try using the /authorize command first!"
                }

            if not check_psnprofile(psn_id):
                return {
                    "content": "Unable to fetch user on PSNProfiles, please check the /howtolink command"
                }

            get_queue().put((user_id, psn_id))
            tasks_left = get_queue().unfinished_tasks

            return {
                "content": f"Queued PSN ID **{psn_id}** for updating, {tasks_left} task(s) pending in queue"
            }
        case "rank":
            if options:
                user_id = options[0]["value"]
                member_user = cmd_data["resolved"]["users"][user_id]

            if (
                rank_user := find_and_rank(get_db().get_all(), user_id)
            ) is None:
                return {
                    "content": "No ranks found, try using the /authorize or /refresh commands."
                }

            rank, user = rank_user

            discord_id = user["discord_id"]

            embed = {
                "author": {
                    "name": f"{member_user['username']}#{member_user['discriminator']}'s Trophies",
                    "icon_url": get_avatar(member_user),
                },
                "type": "rich",
                "color": TROPHY_COLOR_CODE,
                "fields": [],
            }

            for trophy, representation in TROPHY_REPRESENTATION.items():
                value = (
                    f"{representation} **{trophy.title()}** `{user[trophy]}`"
                )

                if trophy == TROPHY_CHECK:
                    value += f" (**`#{rank}`**)"

                embed["fields"].append({"name": "", "value": value})

            return {"embeds": [embed]}
        case "leaderboard":
            return get_leaderboard()

    raise ValueError(f"Invalid command {cmd}")


def execute_component_json(data):
    action, page = data["custom_id"].split("_")

    page = int(page)

    match action:
        case "right":
            return get_leaderboard(page + 1)
        case "left":
            return get_leaderboard(page - 1)

    raise ValueError("Invalid event")


@app.route("/interactions", methods=["POST"])
@validate_discord_request
def slash_command():
    match request.json["type"]:
        case discord.InteractionType.PING:
            return {"type": discord.InteractionCallbackType.PONG}
        case discord.InteractionType.APPLICATION_COMMAND:
            data = execute_cmd_json(
                request.json["data"], request.json["member"]
            )

            # Disable any mentions
            data["allowed_mentions"] = {"parse": []}

            return {
                "type": discord.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": data,
            }
        case discord.InteractionType.MESSAGE_COMPONENT:
            data = execute_component_json(request.json["data"])

            return {
                "type": discord.InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                "data": data,
            }


# This endpoint is called outside the context of discord slash commands
@app.route("/authorize", methods=["PUT", "OPTIONS"])
def authorize():
    # CORS stuff for frontend
    if request.method == "OPTIONS":
        return {}, 200, CORS_HEADERS

    if (token := request.args.get("token")) is None:
        abort(400, "No token specified")

    api = discord.API(token, bot=False)

    user_id = api.get_user().id

    try:
        conn = next(
            filter(
                lambda conn: conn.type == "playstation", api.get_connections()
            )
        )
    except StopIteration:
        abort(400, "PlayStation Network account not linked")

    get_db().set_id_to_psn(user_id, conn.name)
    get_queue().put((user_id, conn.name))

    return {"user_id": user_id, "psn_name": conn.name}, 200, CORS_HEADERS


@app.route("/check", methods=["GET", "OPTIONS"])
def check():
    if request.method == "OPTIONS":
        return {}, 200, CORS_HEADERS

    if (user_id := request.args.get("user_id")) is None:
        abort(400, "No user specified")

    if (psn_id := get_db().get_id_to_psn(user_id)) is None:
        abort(400, "PSN ID not linked")

    if not check_psnprofile(psn_id):
        abort(
            400,
            "Failed to fetch PSNProfiles user, check the /howtolink command on Discord",
        )

    return {}, 200, CORS_HEADERS


def run(public_key, auth_url, port, debug=False):
    app.config["PUBLIC_KEY"] = public_key
    app.config["AUTHORIZATION_URL"] = auth_url

    # JSON error handlers
    for code in [400, 404, 405, 500]:
        app.register_error_handler(
            code, lambda error: ({"error": str(error)}, code, CORS_HEADERS)
        )

    if debug:
        app.run(port=port)
    else:
        serve(app, port=port)
