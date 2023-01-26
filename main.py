import json
import logging
import threading
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


def main():
    logging.getLogger().setLevel(logging.INFO)

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        with open(CONFIG_FILE, "w") as f:
            f.write(json.dumps(CONFIG_DICT, indent=4))
            logging.info(f"Dumped default config to {CONFIG_FILE}")

            return

    scraper_thread = threading.Thread(
        target=scrape_worker.run,
        args=(
            config["token"],
            config["refresh_interval_hours"],
            config["roles_threshold"],
            config["guilds"],
            flask_api.get_queue(),
            flask_api.get_db().get_id_to_psn_batch,
            flask_api.get_db().set_id_to_trophies_batch,
        ),
    )
    scraper_thread.start()

    flask_api.run()


if __name__ == "__main__":
    main()
