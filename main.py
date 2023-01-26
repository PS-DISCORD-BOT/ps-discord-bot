import json
import logging
import sys
import threading
from os import _exit
from queue import Queue

import backend.flask_api as flask_api
import backend.scrape_worker as scrape_worker

CONFIG_FILE = "config.json"

CONFIG_DICT = {
    "token": "my-secret-token",
    "guilds": [],
    "refresh_interval_hours": 12,
    "roles_threshold": {
        "Plathunter - I": 1,
        "Plathunter - II": 10,
        "Plathunter - III": 50,
    },
}

# Exit the program if any thread crashes
def set_excepthooks():
    orig_threading_hook, orig_sys_hook = threading.excepthook, sys.excepthook

    def threading_excepthook(args):
        orig_threading_hook(args)
        _exit(1)

    def sys_excepthook(*args):
        orig_sys_hook(*args)
        _exit(1)

    threading.excepthook, sys.excepthook = threading_excepthook, sys_excepthook


def main():
    set_excepthooks()

    logging.getLogger().setLevel(logging.INFO)

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        with open(CONFIG_FILE, "w") as f:
            f.write(json.dumps(CONFIG_DICT, indent=4))
            logging.info(f"Dumped default config to {CONFIG_FILE}")

            return

    db, queue = flask_api.get_db_queue()

    scraper_thread = threading.Thread(
        target=scrape_worker.run,
        args=(
            config["token"],
            config["refresh_interval_hours"],
            config["roles_threshold"],
            config["guilds"],
            queue,
            db.get_id_to_psn_batch,
            db.set_id_to_trophies_batch,
        ),
    )
    scraper_thread.start()

    flask_api.run()


if __name__ == "__main__":
    main()
