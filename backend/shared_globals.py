from queue import Queue

from backend.dao import Database

DB = "database.db"

TROPHY_CHECK = "platinum"
TROPHY_COLOR_CODE = 0xE5E4E2

queue = Queue()
db = Database(DB)


def get_queue():
    return queue


def get_db():
    return db
