from functools import wraps

import lib.discord as discord
from flask import Flask, Response, abort, g, jsonify, request
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from waitress import serve

from backend.shared_globals import (
    TROPHY_CHECK,
    TROPHY_COLOR_CODE,
    get_db,
    get_queue,
)

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


def execute_cmd_json(cmd_data, member_data):
    cmd = cmd_data["name"]
    user_id = member_data["user"]["id"]

    match cmd:
        case "authorize":
            return {
                "content": "**NOTE**: You must first enlist your account on https://psnprofiles.com by entering your name and hitting **Update User**. The following link can then be used to authorize with the bot:",
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
        case "refresh":
            if (psn_id := get_db().get_id_to_psn(user_id)) is None:
                return {
                    "content": "It seems you haven't authorized your account yet, try using the /authorize command first!"
                }

            get_queue().put((user_id, psn_id))
            tasks_left = get_queue().unfinished_tasks

            return {
                "content": f"Queued PSN ID **{psn_id}** for updating, {tasks_left} task(s) pending in queue"
            }
        case "leaderboard":
            descending_users = sorted(
                get_db().get_all(),
                key=lambda item: item[TROPHY_CHECK],
                reverse=True,
            )

            embed = {
                "title": f"{TROPHY_CHECK.title()} Trophy Leaderboard",
                "type": "rich",
                "color": TROPHY_COLOR_CODE,
                "fields": [],
            }

            for idx, user in enumerate(descending_users[:10]):
                discord_id = user["discord_id"]
                trophies = user[TROPHY_CHECK]

                value = f"{RANK_REPRESENTATION[idx + 1]} `{trophies}` <@{discord_id}>"

                embed["fields"].append({"name": "", "value": value})

            return {"embeds": [embed]}

    raise ValueError(f"Invalid command {cmd}")


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


def run(public_key, auth_url, port, debug=False):
    app.config["PUBLIC_KEY"] = public_key
    app.config["AUTHORIZATION_URL"] = auth_url

    # JSON error handlers
    for code in [400, 404, 405, 500]:
        app.register_error_handler(
            code, lambda error: ({"error": str(error)}, code)
        )

    if debug:
        app.run(port=port)
    else:
        serve(app, port=port)
