import json
import logging

CONFIG_FILE = "config.json"

CONFIG_DICT = {
    "token": "my-secret-token",
    "roles_threshold": {
        1: "Plathunter - I",
        10: "Plathunter - II",
        50: "Plathunter - III",
    },
}


def main():
    logging.getLogger().setLevel(logging.INFO)

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.loads(f.read())
    except FileNotFoundError:
        with open(CONFIG_FILE, "w") as f:
            f.write(json.dumps(CONFIG_DICT))
            logging.info(f"Dumped default config to {CONFIG_FILE}")

            return


if __name__ == "__main__":
    main()
