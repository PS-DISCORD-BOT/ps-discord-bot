import json
import logging
import threading

import backend.flask_api as flask_api
import backend.scrape_worker as scrape_worker

CONFIG_FILE = "config.json"

CONFIG_DICT = {
    "token": "my-secret-token",
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

    flask_thread = threading.Thread(target=flask_api.run)
    flask_thread.start()

    scrape_worker.run(
        config["token"],
        config["refresh_interval_hours"],
        config["roles_threshold"],
    )

    flask_thread.join()


if __name__ == "__main__":
    main()
