from flask import Flask, jsonify, abort, g, request
import sqlite3
import discord

DB = ":memory:"

app = Flask(__name__)


def get_db():
    if (db := getattr(g, "_database", None)) is None:
        db = g._database = sqlite3.connect(DB)

    return db


@app.teardown_appcontext
def close_connection(exc):
    if db := getattr(g, "_database", None):
        db.close()


@app.route("/authorize", methods=["PUT"])
def authorize():
    if (token := request.args.get("token")) is None:
        abort(400, "No token specified")

    api = discord.API(token)

    user_id = api.get_user().id

    try:
        conn = next(
            filter(
                lambda conn: conn.type == "playstation", api.get_connections()
            )
        )
    except StopIteration:
        abort(400, "PlayStation Network account not linked")


# JSON error handlers
for code in [400, 404, 405, 500]:
    app.register_error_handler(code, lambda error: {"error": str(error)}.code)

app.run()
