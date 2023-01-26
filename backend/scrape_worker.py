import logging
import sys
from dataclasses import asdict
from queue import Empty, Queue
from time import sleep, time
from typing import Callable

import lib.discord as discord
from lib.roles import Roles
from lib.scraper import fetch_trophies


def scrape(id_to_psn):
    id_to_trophies = {}

    for id, psn in id_to_psn.items():
        logging.info(f"Scraping trophies for PSN user {psn}")

        # Convert the dataclass to a dict: {"total": ..., "gold": ...}
        try:
            id_to_trophies[id] = asdict(fetch_trophies(psn))
        except Exception:
            logging.critical(
                f"Failed to scrape trophies for PSN user {psn}",
                exc_info=sys.exc_info(),
            )

        sleep(1)  # TODO is this enough for rate limiting?

    return id_to_trophies


def run(
    token: str,
    refresh_interval_hours: int,
    roles_threshold: dict,
    guilds: list,
    instant_update_queue: Queue,
    id_to_psn_batch_get: Callable,
    id_to_trophies_batch_set: Callable,
):
    api = discord.API(token, bot=True)
    roles_syncer = Roles(api, roles_threshold)

    def sync(id_to_trophies):
        for guild in guilds:
            logging.info(f"Syncing roles for guild {guild}")

            try:
                roles_syncer.sync_roles(guild, id_to_trophies)
            except Exception:
                logging.critical(
                    f"Failed to sync roles for guild {guild}",
                    exc_info=sys.exc_info(),
                )

    start_time = time()

    while True:
        try:
            instant_id, instant_psn = instant_update_queue.get(block=False)
            id_to_trophies = scrape({instant_id: instant_psn})

            id_to_trophies_batch_set(id_to_trophies)
            sync(id_to_trophies)
        except Empty:
            pass

        sleep(10)

        # Time elapsed (in seconds) >= interval (in seconds)
        if (time() - start_time) >= (refresh_interval_hours * 60 * 60):
            start_time = time()

            id_to_trophies = scrape(id_to_psn_batch_get())

            id_to_trophies_batch_set(id_to_trophies)
            sync(id_to_trophies)
