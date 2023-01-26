from queue import Queue

from flask import Flask, abort, g, jsonify, request

import backend.dao as dao
import lib.discord as discord

DB = ":memory:"

app = Flask(__name__)


def get_db():
    if (db := getattr(g, "_database", None)) is None:
        db = g._database = dao.Database(DB)

    return db


def get_queue():
    if (queue := getattr(g, "_queue", None)) is None:
        queue = g._queue = Queue()

    return queue


# For external use
def get_db_queue():
    with app.app_context():
        return get_db(), get_queue()


@app.teardown_appcontext
def close_connection(exc):
    if db := getattr(g, "_database", None):
        db.close()


@app.route("/authorize", methods=["PUT"])
def authorize():
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

    return {"user_id": user_id, "psn_name": conn.name}, 200


def run():
    # JSON error handlers
    for code in [400, 404, 405, 500]:
        app.register_error_handler(
            code, lambda error: ({"error": str(error)}, code)
        )

    app.run()
