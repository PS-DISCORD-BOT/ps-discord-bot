from queue import Queue

from backend.dao import Database

DB = ":memory:"

queue = Queue()
db = Database(DB)


def get_queue():
    return queue


def get_db():
    return db
