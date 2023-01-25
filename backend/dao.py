import sqlite3
from contextlib import contextmanager


class Ensure:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()


class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        self.cur = self.conn.cursor()

        self._create()

    def _create(self):
        with Ensure(self.conn):
            ...

    def close(self):
        self.conn.close()
